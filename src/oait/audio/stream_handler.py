"""Audio stream handler for capturing and processing audio."""

import logging
import asyncio
from typing import Optional, Callable
from collections import deque
from collections.abc import Deque
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


class AudioStreamHandler:
    """Handles audio stream capture and processing."""

    def __init__(
        self,
        sample_rate: int = 16000,
        chunk_duration: float = 1.0,
    ):
        """Initialize audio stream handler.

        Args:
            sample_rate: Audio sample rate in Hz
            chunk_duration: Duration of each audio chunk in seconds
        """
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.chunk_size = int(sample_rate * chunk_duration)
        self.is_running = False
        self.audio_queue: asyncio.Queue = asyncio.Queue()
        self.on_audio_callback: Optional[Callable] = None

    async def start(self) -> None:
        """Start capturing audio."""
        self.is_running = True
        logger.info("Audio stream started")

    async def stop(self) -> None:
        """Stop capturing audio."""
        self.is_running = False
        logger.info("Audio stream stopped")

    async def capture_audio(self) -> Optional[np.ndarray]:
        """Capture an audio chunk from the stream.

        Returns:
            Audio data as numpy array, or None if queue is empty
        """
        try:
            audio_data = await asyncio.wait_for(self.audio_queue.get(), timeout=0.1)
            return audio_data
        except asyncio.TimeoutError:
            return None

    async def push_audio(self, audio_data: np.ndarray) -> None:
        """Push audio data to the processing queue.

        Args:
            audio_data: Audio data as numpy array
        """
        await self.audio_queue.put(audio_data)


class TranscriptBuffer:
    """Manages a sliding window of transcripts."""

    def __init__(self, duration: float = 30.0):
        """Initialize transcript buffer.

        Args:
            duration: Duration of the sliding window in seconds
        """
        self.duration = duration
        self.buffer: Deque = deque()

    def append(self, text: str, timestamp: Optional[float] = None) -> None:
        """Add a transcript to the buffer.

        Args:
            text: Transcript text
            timestamp: Optional timestamp (uses current time if not provided)
        """
        if timestamp is None:
            timestamp = datetime.now().timestamp()

        self.buffer.append({"text": text, "timestamp": timestamp})
        self._cleanup()

    def get_recent(self, duration: Optional[float] = None) -> list:
        """Get recent transcripts within the specified duration.

        Args:
            duration: Duration to look back (uses buffer duration if not specified)

        Returns:
            List of transcript entries
        """
        if duration is None:
            duration = self.duration

        cutoff = datetime.now().timestamp() - duration
        return [entry for entry in self.buffer if entry["timestamp"] > cutoff]

    def get_all(self) -> list:
        """Get all transcripts in the buffer.

        Returns:
            List of all transcript entries
        """
        return self.buffer.copy()

    def clear(self) -> None:
        """Clear all transcripts from the buffer."""
        self.buffer.clear()

    def _cleanup(self) -> None:
        """Remove entries older than the buffer duration."""
        cutoff = datetime.now().timestamp() - self.duration
        while self.buffer and self.buffer[0]["timestamp"] < cutoff:
            self.buffer.popleft()


class SilenceDetector:
    """Detects silence in audio stream."""

    def __init__(self, threshold: float = 3.0):
        """Initialize silence detector.

        Args:
            threshold: Silence duration threshold in seconds
        """
        self.threshold = threshold
        self.last_speech_time: Optional[float] = None
        self.is_silent = False

    def update(self, has_speech: bool) -> None:
        """Update silence state.

        Args:
            has_speech: Whether speech was detected in the current chunk
        """
        current_time = datetime.now().timestamp()

        if has_speech:
            self.last_speech_time = current_time
            self.is_silent = False
        elif self.last_speech_time is not None:
            silence_duration = current_time - self.last_speech_time
            self.is_silent = silence_duration > self.threshold

    def get_silence_duration(self) -> float:
        """Get current silence duration.

        Returns:
            Duration of silence in seconds
        """
        if self.last_speech_time is None:
            return 0.0

        current_time = datetime.now().timestamp()
        return max(0.0, current_time - self.last_speech_time)

    def reset(self) -> None:
        """Reset the silence detector."""
        self.last_speech_time = None
        self.is_silent = False
