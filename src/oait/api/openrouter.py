"""OpenRouter API client for LLM interactions."""

import logging
import json
from typing import Dict, List, Optional, Any, Callable, Awaitable
import httpx
from PIL import Image
import base64
import io

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """Client for OpenRouter API (OpenAI-compatible).
    
    Tool Calling Flow (per OpenRouter docs):
    1. Send request with `tools` parameter - model responds with `tool_calls`
    2. Execute tool locally (client-side)
    3. Send result back with `role: "tool"` message and `tool_call_id`
    Note: `tools` must be included in EVERY request for the router to validate
    """

    def __init__(self, api_key: str, model: str = "google/gemini-3.0-pro"):
        """Initialize the OpenRouter client.

        Args:
            api_key: OpenRouter API key
            model: Model to use (default: Gemini 3 Pro)
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/raymondclowe/OAIT",
            "X-Title": "OAIT - Observational AI Tutor",
        }

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str | Dict[str, Any]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Send a chat completion request.

        Args:
            messages: List of message dicts with 'role' and 'content'
            tools: Optional list of tool definitions for function calling
            tool_choice: "auto", "none", or {"type": "function", "function": {"name": "..."}}
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Response dict from the API
        """
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        if tools:
            payload["tools"] = tools
        
        if tool_choice:
            payload["tool_choice"] = tool_choice

        if max_tokens:
            payload["max_tokens"] = max_tokens

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                logger.debug(f"[OpenRouter] Sending request to {self.model}")
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                logger.debug(f"[OpenRouter] Response: finish_reason={result.get('choices', [{}])[0].get('finish_reason')}")
                return result
            except httpx.HTTPError as e:
                logger.error(f"OpenRouter API error: {e}")
                raise

    async def chat_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        tool_handlers: Dict[str, Callable[..., Awaitable[Any]]],
        temperature: float = 0.7,
        max_iterations: int = 5,
    ) -> Dict[str, Any]:
        """Send a chat request and automatically handle tool calls.
        
        This implements the OpenRouter tool calling flow:
        1. Send request with tools
        2. If model requests tool_calls, execute them locally
        3. Send results back and repeat until model gives final response
        
        Args:
            messages: Initial messages (will be mutated with tool results)
            tools: Tool definitions (OpenAI function calling format)
            tool_handlers: Dict mapping tool names to async handler functions
            temperature: Sampling temperature
            max_iterations: Max tool call iterations to prevent infinite loops
            
        Returns:
            Final response from the model
        """
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Make API call with tools
            response = await self.chat(
                messages=messages,
                tools=tools,
                temperature=temperature,
            )
            
            choice = response.get("choices", [{}])[0]
            message = choice.get("message", {})
            finish_reason = choice.get("finish_reason")
            
            # Check if model wants to call tools
            tool_calls = message.get("tool_calls", [])
            
            if not tool_calls or finish_reason == "stop":
                # No tool calls - return final response
                logger.info(f"[OpenRouter] Final response after {iteration} iterations")
                return response
            
            # Model requested tool calls - process them
            logger.info(f"[OpenRouter] Processing {len(tool_calls)} tool calls")
            
            # Add assistant message with tool_calls to conversation
            messages.append({
                "role": "assistant",
                "content": message.get("content"),  # May be null
                "tool_calls": tool_calls,
            })
            
            # Execute each tool call
            for tool_call in tool_calls:
                tool_id = tool_call.get("id", "")
                function_info = tool_call.get("function", {})
                tool_name = function_info.get("name", "")
                arguments_str = function_info.get("arguments", "{}")
                
                logger.info(f"[OpenRouter] Executing tool: {tool_name}")
                
                try:
                    # Parse arguments
                    arguments = json.loads(arguments_str)
                    
                    # Find and execute handler
                    if tool_name in tool_handlers:
                        result = await tool_handlers[tool_name](**arguments)
                        result_str = json.dumps(result) if not isinstance(result, str) else result
                    else:
                        logger.warning(f"[OpenRouter] Unknown tool: {tool_name}")
                        result_str = json.dumps({"error": f"Unknown tool: {tool_name}"})
                    
                except json.JSONDecodeError as e:
                    logger.error(f"[OpenRouter] Failed to parse tool arguments: {e}")
                    result_str = json.dumps({"error": f"Invalid arguments: {e}"})
                except Exception as e:
                    logger.error(f"[OpenRouter] Tool execution error: {e}")
                    result_str = json.dumps({"error": str(e)})
                
                # Add tool result to messages
                # IMPORTANT: Must use 'tool_call_id' to match the request
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_id,
                    "content": result_str,
                })
        
        logger.warning(f"[OpenRouter] Max iterations ({max_iterations}) reached")
        return response

    async def vision(
        self,
        image: Image.Image,
        prompt: str,
        context: Optional[str] = None,
    ) -> str:
        """Analyze an image with vision capabilities.

        Args:
            image: PIL Image to analyze
            prompt: Prompt describing what to analyze
            context: Optional additional context

        Returns:
            Analysis text from the model
        """
        # Convert image to base64
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_base64 = base64.b64encode(buffer.getvalue()).decode()

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_base64}"},
                    },
                ],
            }
        ]

        if context:
            messages.insert(
                0,
                {"role": "system", "content": context},
            )

        response = await self.chat(messages=messages)

        try:
            return response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse vision response: {e}")
            raise

