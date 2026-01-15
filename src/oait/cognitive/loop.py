"""OODA loop implementation for cognitive processing."""

import logging
import asyncio
from typing import Optional
from datetime import datetime
from ..models.data_models import (
    SessionState,
    StudentModel,
    Observation,
    Analysis,
    Decision,
    InternalMonologue,
    StudentState,
    ActionDecision,
)
from ..api.openrouter import OpenRouterClient
from .triggers import TriggerDetector

logger = logging.getLogger(__name__)


class OODALoop:
    """Observe-Orient-Decide-Act cognitive loop."""

    def __init__(
        self,
        openrouter_client: OpenRouterClient,
        trigger_detector: TriggerDetector,
    ):
        """Initialize OODA loop.

        Args:
            openrouter_client: OpenRouter API client
            trigger_detector: Trigger detector instance
        """
        self.client = openrouter_client
        self.trigger_detector = trigger_detector
        self.is_running = False

    async def generate_internal_monologue(
        self,
        observation: Observation,
        student_model: StudentModel,
        session_state: SessionState,
    ) -> dict:
        """Generate internal monologue about student state using LLM.

        Args:
            observation: Current observation
            student_model: Student model
            session_state: Current session state

        Returns:
            LLM response with analysis and decision
        """
        system_prompt = """You are an expert AI tutor observing a student working on a problem.
        
Your role is to:
1. Analyze what the student is doing
2. Determine if they need help
3. Decide whether to intervene or continue observing

Think carefully about pedagogical best practices:
- Don't interrupt if the student is making progress
- Wait for them to struggle briefly before helping
- Use Socratic questioning when appropriate
- Only intervene when truly necessary

Respond with your internal analysis and decision."""

        user_prompt = f"""Current Observation:
- Visual: {observation.visual}
- Audio: {observation.audio}
- Context: {observation.context}

Student Profile:
- Patience Level: {student_model.pedagogy_profile.patience_level}
- Learning Style: {student_model.pedagogy_profile.preferred_learning_style}

Session State:
- Silence Duration: {session_state.silence_duration} seconds
- Last Intervention: {session_state.last_intervention_time} seconds ago

Analyze the situation and decide what to do."""

        # Note: In production, sanitize observation data to prevent prompt injection
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = await self.client.chat(messages=messages, temperature=0.3)
        return response

    async def observe(self, session_state: SessionState) -> Observation:
        """Observe phase: Gather current state.

        Args:
            session_state: Current session state

        Returns:
            Observation object
        """
        # Aggregate visual data
        visual = "Whiteboard content"  # Placeholder
        if session_state.current_problem_image:
            visual = f"Image captured at {session_state.last_significant_change}"

        # Aggregate audio data
        recent_transcripts = session_state.get_recent_transcripts(10.0)
        audio = " ".join([t.text for t in recent_transcripts]) if recent_transcripts else ""

        # Create observation
        observation = Observation(
            visual=visual,
            audio=audio,
            context={
                "silence_duration": session_state.silence_duration,
                "is_speaking": session_state.student_is_speaking,
                "is_writing": session_state.student_is_writing,
            },
        )

        logger.info(f"[OBSERVE] visual='{visual[:50]}...' audio='{audio[:100] if audio else '(none)'}' silence={session_state.silence_duration:.1f}s")
        return observation

    async def orient(
        self,
        observation: Observation,
        student_model: StudentModel,
        session_state: SessionState,
    ) -> Analysis:
        """Orient phase: Analyze the observation.

        Args:
            observation: Current observation
            student_model: Student model
            session_state: Session state

        Returns:
            Analysis object
        """
        # For MVP, use simple heuristics
        # Later, can use LLM for more sophisticated analysis

        analysis = Analysis(
            student_state=StudentState.ENGAGED,
            error_detected=False,
            explicit_question="?" in observation.audio,
            confidence=0.5,
        )

        # Check for confusion indicators
        if session_state.silence_duration > 5.0:
            analysis.student_state = StudentState.STUCK
            analysis.confidence = 0.7

        logger.info(f"[ORIENT] state={analysis.student_state.value} confidence={analysis.confidence:.2f} explicit_q={analysis.explicit_question}")
        return analysis

    async def decide(
        self,
        analysis: Analysis,
        student_model: StudentModel,
        session_state: SessionState,
    ) -> Decision:
        """Decide phase: Determine what action to take.

        Args:
            analysis: Current analysis
            student_model: Student model
            session_state: Session state

        Returns:
            Decision object
        """
        # Priority 1: Explicit question
        if analysis.explicit_question:
            decision = Decision(
                action=ActionDecision.SPEAK,
                reasoning="Student asked an explicit question",
                confidence=0.9,
            )
            decision.response_text = await self._generate_response(
                analysis, student_model, session_state, decision
            )
            logger.info(f"[DECIDE] action=SPEAK reason='explicit question' response='{decision.response_text[:50]}...'")
            return decision

        # Priority 2: Extended stuck state
        if (
            analysis.student_state == StudentState.STUCK
            and session_state.silence_duration > student_model.pedagogy_profile.optimal_intervention_delay * 2
        ):
            decision = Decision(
                action=ActionDecision.SPEAK,
                reasoning="Student appears stuck for extended period",
                confidence=0.7,
            )
            decision.response_text = await self._generate_response(
                analysis, student_model, session_state, decision
            )
            logger.info(f"[DECIDE] action=SPEAK reason='stuck' response='{decision.response_text[:50]}...'")
            return decision

        # Default: Wait and observe more
        decision = Decision(
            action=ActionDecision.WAIT,
            reasoning="Student appears to be working, continue observing",
            confidence=analysis.confidence,
        )
        logger.info(f"[DECIDE] action={decision.action.value} reason='{decision.reasoning}'")
        return decision

    async def _generate_response(
        self,
        analysis: Analysis,
        student_model: StudentModel,
        session_state: SessionState,
        decision: Decision,
    ) -> str:
        """Generate intervention response using LLM.
        
        Args:
            analysis: Current analysis
            student_model: Student model  
            session_state: Session state
            decision: The decision made
            
        Returns:
            Response text to speak to student
        """
        recent = session_state.get_recent_transcripts(30.0)
        transcript_text = " ".join([t.text for t in recent]) if recent else "No recent speech"
        
        system_prompt = """You are a patient, supportive AI math tutor. 
Generate a brief, helpful response based on the student's current state.
Use Socratic questioning when appropriate. Be encouraging but concise.
Keep responses to 1-2 sentences."""

        user_prompt = f"""Student state: {analysis.student_state.value}
Intervention reason: {decision.reasoning}
Recent transcript: {transcript_text}
Learning style: {student_model.pedagogy_profile.preferred_learning_style.value}

Generate a short, helpful response:"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        try:
            response = await self.client.chat(messages=messages, temperature=0.7)
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            return content if content else "I notice you might need some help. What are you working on?"
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I notice you might need some help. What are you working on?"

    async def act(self, decision: Decision, session_state: SessionState) -> None:
        """Act phase: Execute the decision.

        Args:
            decision: Decision to execute
            session_state: Session state
        """
        logger.info(f"Action: {decision.action} - {decision.reasoning}")

        if decision.action == ActionDecision.SPEAK:
            # For MVP, just log the intervention
            # Later, integrate TTS
            logger.info("INTERVENTION: Would speak to student here")
            session_state.last_intervention_time = datetime.now().timestamp()

        elif decision.action == ActionDecision.UPDATE_DB:
            # Update student model
            logger.info("Updating student model with observations")

        elif decision.action == ActionDecision.WAIT:
            # Continue observing
            pass

    async def run_cycle(
        self,
        session_state: SessionState,
        student_model: StudentModel,
    ) -> Optional[InternalMonologue]:
        """Run one OODA cycle.

        Args:
            session_state: Current session state
            student_model: Student model

        Returns:
            Internal monologue if cycle completed, None otherwise
        """
        logger.info("="*60)
        logger.info("[OODA CYCLE START]")
        try:
            # Observe
            observation = await self.observe(session_state)

            # Orient
            analysis = await self.orient(observation, student_model, session_state)

            # Decide
            decision = await self.decide(analysis, student_model, session_state)

            # Act
            await self.act(decision, session_state)

            # Create internal monologue
            monologue = InternalMonologue(
                observation=observation,
                analysis=analysis,
                decision=decision,
            )

            # Store in session state
            session_state.add_monologue(monologue)

            logger.info(f"[OODA CYCLE END] action={decision.action.value}")
            logger.info("="*60)
            return monologue

        except Exception as e:
            logger.error(f"OODA cycle error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

    async def start(self, session_state: SessionState, student_model: StudentModel) -> None:
        """Start the OODA loop.

        Args:
            session_state: Session state
            student_model: Student model
        """
        self.is_running = True
        logger.info("OODA loop started")

        while self.is_running:
            # Check triggers
            should_trigger, reasons = self.trigger_detector.check_triggers(session_state)

            if should_trigger:
                logger.info(f"Running OODA cycle, triggers: {reasons}")
                await self.run_cycle(session_state, student_model)

            # Wait before next check
            await asyncio.sleep(1.0)

    async def stop(self) -> None:
        """Stop the OODA loop."""
        self.is_running = False
        logger.info("OODA loop stopped")
