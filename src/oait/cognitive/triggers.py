"""Trigger detection for OODA loop activation."""

import logging
from typing import List
from datetime import datetime
from ..models.data_models import SessionState

logger = logging.getLogger(__name__)


class TriggerDetector:
    """Detects triggers that should activate the OODA loop."""

    def __init__(
        self,
        silence_threshold: float = 3.0,
        change_threshold: float = 0.1,
    ):
        """Initialize trigger detector.

        Args:
            silence_threshold: Silence duration to trigger analysis (seconds)
            change_threshold: Visual change magnitude to trigger analysis
        """
        self.silence_threshold = silence_threshold
        self.change_threshold = change_threshold

    def check_triggers(
        self,
        session_state: SessionState,
        has_visual_change: bool = False,
    ) -> tuple[bool, List[str]]:
        """Check if any triggers are activated.

        Args:
            session_state: Current session state
            has_visual_change: Whether significant visual change detected

        Returns:
            Tuple of (should_trigger, list_of_reasons)
        """
        triggers: List[str] = []

        # Trigger 1: Extended silence
        if session_state.silence_duration > self.silence_threshold:
            triggers.append(f"silence_{session_state.silence_duration:.1f}s")

        # Trigger 2: Significant whiteboard change
        if has_visual_change:
            triggers.append("whiteboard_change")

        # Trigger 3: Explicit question detected
        # (Would need NLP to detect questions in transcript)
        recent_transcripts = session_state.get_recent_transcripts(5.0)
        if recent_transcripts:
            last_text = recent_transcripts[-1].text if recent_transcripts else ""
            if "?" in last_text or any(
                q in last_text.lower() for q in ["how do", "what is", "can you", "help"]
            ):
                triggers.append("explicit_question")

        # Trigger 4: First analysis (no previous monologue)
        if not session_state.ai_internal_monologue:
            triggers.append("initial_analysis")

        should_trigger = len(triggers) > 0

        if should_trigger:
            logger.info(f"Triggers activated: {', '.join(triggers)}")

        return should_trigger, triggers
