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

        logger.debug(f"Observation: visual={bool(visual)}, audio={bool(audio)}")
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

        logger.debug(f"Analysis: state={analysis.student_state}, confidence={analysis.confidence}")
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
            return Decision(
                action=ActionDecision.SPEAK,
                reasoning="Student asked an explicit question",
                confidence=0.9,
            )

        # Priority 2: Extended stuck state
        if (
            analysis.student_state == StudentState.STUCK
            and session_state.silence_duration > student_model.pedagogy_profile.optimal_intervention_delay * 2
        ):
            return Decision(
                action=ActionDecision.SPEAK,
                reasoning="Student appears stuck for extended period",
                confidence=0.7,
            )

        # Default: Wait and observe more
        return Decision(
            action=ActionDecision.WAIT,
            reasoning="Student appears to be working, continue observing",
            confidence=analysis.confidence,
        )

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

            return monologue

        except Exception as e:
            logger.error(f"OODA cycle error: {e}")
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
