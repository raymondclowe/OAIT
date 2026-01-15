"""Tool-based OODA loop implementation.

This is the new AI-controlled cognitive loop that uses function calling
to let the AI decide what to observe and when to act.
"""

import logging
import asyncio
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from ..api.openrouter import OpenRouterClient
from ..models.data_models import SessionState, StudentModel
from ..tools.ai_tools import (
    ALL_TOOLS,
    AIToolHandlers,
    ToolContext,
    AI_TUTOR_SYSTEM_PROMPT,
)

logger = logging.getLogger(__name__)


@dataclass
class ToolOODAResult:
    """Result from a tool-based OODA cycle."""
    cycle_number: int
    tools_called: List[str] = field(default_factory=list)
    observations: Dict[str, Any] = field(default_factory=dict)
    final_action: Optional[str] = None
    reasoning: Optional[str] = None
    spoke_to_student: bool = False
    spoken_text: Optional[str] = None


class ToolOODALoop:
    """AI-controlled OODA loop using function calling.
    
    The AI uses tools to:
    1. Observe (get_audio_transcript, get_whiteboard, get_session_status)
    2. Orient & Decide (internal reasoning with tool results)
    3. Act (speak, update_student_model, wait_for_event)
    
    The AI is fully in control of the observation cycle.
    """
    
    def __init__(
        self,
        openrouter_client: OpenRouterClient,
        context: ToolContext,
    ):
        """Initialize the tool-based OODA loop.
        
        Args:
            openrouter_client: OpenRouter API client
            context: Tool context with all dependencies
        """
        self.client = openrouter_client
        self.context = context
        self.handlers = AIToolHandlers(context)
        self.cycle_count = 0
        self.message_history: List[Dict[str, Any]] = []
        self.is_running = False
        
        # Mode settings
        self._observation_interval = 5.0
        self._mode = "active"
    
    def _build_initial_prompt(self) -> str:
        """Build the initial prompt for a new cycle."""
        return """A new observation cycle is starting. 

First, use get_session_status to understand the current state.
Then use get_audio_transcript to hear what the student said.
Based on what you find, decide whether to:
- Use get_whiteboard if the student is working on something visual
- Use speak if they asked a question or need help
- Use wait_for_event if they're working and don't need intervention
- Use update_student_model if you learned something about them

End each cycle by calling end_observation_cycle with your decision."""
    
    async def run_cycle(self) -> ToolOODAResult:
        """Run one tool-based OODA cycle.
        
        The AI uses tools to observe, analyze, and decide what to do.
        
        Returns:
            ToolOODAResult with details of what happened
        """
        self.cycle_count += 1
        result = ToolOODAResult(cycle_number=self.cycle_count)
        
        logger.info("=" * 60)
        logger.info(f"[TOOL-OODA] Starting cycle #{self.cycle_count}")
        
        try:
            # Build messages for this cycle
            messages = [
                {"role": "system", "content": AI_TUTOR_SYSTEM_PROMPT},
                {"role": "user", "content": self._build_initial_prompt()},
            ]
            
            # Add recent conversation context if available
            if self.message_history:
                # Include last few exchanges for context
                recent = self.message_history[-4:]  # Last 2 exchanges
                messages = messages[:1] + recent + messages[1:]
            
            # Get tool handlers
            tool_handlers = self.handlers.get_handlers()
            
            # Run the tool calling loop
            max_iterations = 10  # Safety limit
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                logger.debug(f"[TOOL-OODA] Iteration {iteration}")
                
                # Call LLM with tools
                response = await self.client.chat_with_tools(
                    messages=messages,
                    tools=ALL_TOOLS,
                    tool_handlers=tool_handlers,
                    temperature=0.3,
                    max_iterations=1,  # We handle iteration ourselves
                )
                
                if not response:
                    logger.error("[TOOL-OODA] Empty response from LLM")
                    break
                
                # Get the assistant message from response
                choice = response.get("choices", [{}])[0]
                message = choice.get("message", {})
                finish_reason = choice.get("finish_reason")
                
                # Track tool calls
                tool_calls = message.get("tool_calls", [])
                for tc in tool_calls:
                    tool_name = tc.get("function", {}).get("name", "")
                    result.tools_called.append(tool_name)
                    logger.info(f"[TOOL-OODA] Called: {tool_name}")
                    
                    # Track specific actions
                    if tool_name == "speak":
                        result.spoke_to_student = True
                        # The actual text is logged elsewhere
                    elif tool_name == "end_observation_cycle":
                        # Parse the arguments to get the decision
                        import json
                        try:
                            args = json.loads(tc.get("function", {}).get("arguments", "{}"))
                            result.final_action = args.get("next_action")
                            result.reasoning = args.get("reasoning")
                        except:
                            pass
                
                # Add messages to history
                if message.get("content"):
                    self.message_history.append({
                        "role": "assistant",
                        "content": message["content"]
                    })
                
                # Check if cycle should end
                if finish_reason == "stop" or "end_observation_cycle" in result.tools_called:
                    logger.info(f"[TOOL-OODA] Cycle ended: reason={finish_reason}")
                    break
                
                # If there were tool calls, we need to continue
                # The chat_with_tools already handles the tool call -> result flow
                # So if we get here with tool_calls, we should have results appended
                
                # Get the final content if no more tool calls
                content = message.get("content", "")
                if content and not tool_calls:
                    logger.info(f"[TOOL-OODA] Final response: {content[:100]}...")
                    break
            
            logger.info(f"[TOOL-OODA] Cycle complete. Tools called: {result.tools_called}")
            logger.info(f"[TOOL-OODA] Final action: {result.final_action}, Reasoning: {result.reasoning}")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"[TOOL-OODA] Cycle error: {e}")
            import traceback
            logger.error(traceback.format_exc())
        
        return result
    
    async def start(self) -> None:
        """Start the OODA loop running continuously."""
        self.is_running = True
        logger.info("[TOOL-OODA] Starting continuous loop")
        
        while self.is_running:
            try:
                result = await self.run_cycle()
                
                # Adjust interval based on result
                if result.final_action == "observe_again":
                    interval = 2.0
                elif result.final_action == "wait":
                    interval = self._observation_interval
                else:
                    interval = self._observation_interval
                
                # Check if handlers changed the interval
                if hasattr(self.handlers, '_observation_interval'):
                    interval = self.handlers._observation_interval
                
                logger.debug(f"[TOOL-OODA] Sleeping for {interval}s")
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                logger.info("[TOOL-OODA] Loop cancelled")
                break
            except Exception as e:
                logger.error(f"[TOOL-OODA] Loop error: {e}")
                await asyncio.sleep(5.0)  # Back off on error
    
    async def stop(self) -> None:
        """Stop the OODA loop."""
        self.is_running = False
        logger.info("[TOOL-OODA] Stopping loop")
    
    def get_observation_interval(self) -> float:
        """Get current observation interval."""
        return self._observation_interval
    
    def set_observation_interval(self, interval: float) -> None:
        """Set the observation interval."""
        self._observation_interval = interval
