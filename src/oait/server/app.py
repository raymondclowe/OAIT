"""Main server application for OAIT."""

import logging
import asyncio
from pathlib import Path
from ..config import get_settings
from ..models.repository import StudentModelRepository
from ..api.openrouter import OpenRouterClient
from ..audio.whisper_stt import WhisperSTT
from ..audio.stream_handler import TranscriptBuffer, SilenceDetector
from ..vision.analyzer import VisionAnalyzer
from ..vision.preprocessor import ImagePreprocessor
from ..cognitive.loop import OODALoop
from ..cognitive.triggers import TriggerDetector
from ..models.data_models import SessionState
import uuid

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class OAITServer:
    """Main OAIT server application."""

    def __init__(self) -> None:
        """Initialize OAIT server."""
        self.settings = get_settings()
        self.repository: StudentModelRepository | None = None
        self.openrouter_client: OpenRouterClient | None = None
        self.whisper_stt: WhisperSTT | None = None
        self.vision_analyzer: VisionAnalyzer | None = None
        self.ooda_loop: OODALoop | None = None

    async def initialize(self) -> None:
        """Initialize all components."""
        logger.info("Initializing OAIT server...")

        # Ensure directories exist
        Path("./memory").mkdir(exist_ok=True)
        Path("./logs").mkdir(exist_ok=True)

        # Initialize repository
        self.repository = StudentModelRepository(self.settings.sqlite_db_path)
        await self.repository.initialize()

        # Initialize OpenRouter client
        self.openrouter_client = OpenRouterClient(
            api_key=self.settings.openrouter_api_key,
            model=self.settings.openrouter_model,
        )

        # Initialize Whisper STT
        self.whisper_stt = WhisperSTT(
            model_size=self.settings.whisper_model_size,
            device=self.settings.whisper_device,
            compute_type=self.settings.whisper_compute_type,
        )

        # Initialize vision components
        self.vision_analyzer = VisionAnalyzer(self.openrouter_client)

        # Initialize OODA loop
        trigger_detector = TriggerDetector(
            silence_threshold=self.settings.silence_threshold,
            change_threshold=self.settings.vision_change_threshold,
        )
        self.ooda_loop = OODALoop(
            openrouter_client=self.openrouter_client,
            trigger_detector=trigger_detector,
        )

        logger.info("OAIT server initialized successfully")

    async def start_session(self, student_id: str) -> SessionState:
        """Start a new tutoring session.

        Args:
            student_id: ID of the student

        Returns:
            New session state
        """
        if not self.repository:
            raise RuntimeError("Server not initialized")

        logger.info(f"Starting session for student: {student_id}")

        # Load or create student model
        student_model = await self.repository.load(student_id)
        if not student_model:
            logger.info(f"Creating new student model for: {student_id}")
            student_model = await self.repository.create_default_model(student_id)

        # Create session state
        session_state = SessionState(
            session_id=str(uuid.uuid4()),
            student_id=student_id,
        )

        return session_state

    async def run(self) -> None:
        """Run the server."""
        await self.initialize()

        logger.info(f"OAIT server running on {self.settings.server_host}:{self.settings.server_port}")
        logger.info("Press Ctrl+C to stop")

        try:
            # Keep server running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")


async def main() -> None:
    """Main entry point."""
    server = OAITServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
