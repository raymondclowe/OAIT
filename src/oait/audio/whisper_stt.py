"""Local Faster-Whisper speech-to-text service."""

import logging
from typing import Optional, Literal
from faster_whisper import WhisperModel
import numpy as np

logger = logging.getLogger(__name__)


class WhisperSTT:
    """Local Whisper-based speech-to-text service using faster-whisper."""

    def __init__(
        self,
        model_size: Literal["base", "small", "medium", "large"] = "base",
        device: str = "auto",
        compute_type: str = "int8",
    ):
        """Initialize Whisper STT.

        Args:
            model_size: Model size (base, small, medium, large)
            device: Device to use (auto, cpu, cuda)
            compute_type: Computation type (int8, float16, float32)
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model: Optional[WhisperModel] = None
        logger.info(f"Initializing Whisper STT with model={model_size}, device={device}")

    def load_model(self) -> None:
        """Load the Whisper model."""
        if self.model is None:
            logger.info(f"Loading Whisper model: {self.model_size}")
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )
            logger.info("Whisper model loaded successfully")

    async def transcribe(self, audio: np.ndarray, sample_rate: int = 16000) -> str:
        """Transcribe audio to text.

        Args:
            audio: Audio data as numpy array
            sample_rate: Sample rate of audio (default 16000)

        Returns:
            Transcribed text
        """
        if self.model is None:
            self.load_model()

        try:
            # Transcribe with faster-whisper
            segments, info = self.model.transcribe(
                audio,
                language="en",
                beam_size=5,
                vad_filter=True,
            )

            # Combine all segments
            text = " ".join([segment.text.strip() for segment in segments])
            return text

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""

    def unload_model(self) -> None:
        """Unload the model to free memory."""
        if self.model is not None:
            del self.model
            self.model = None
            logger.info("Whisper model unloaded")
