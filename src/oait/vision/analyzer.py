"""Vision analyzer for whiteboard image analysis."""

import logging
from typing import Dict, Any, Optional
import numpy as np
from PIL import Image
from ..api.openrouter import OpenRouterClient

logger = logging.getLogger(__name__)


class VisionAnalyzer:
    """Analyzes whiteboard images using vision LLM."""

    def __init__(self, openrouter_client: OpenRouterClient):
        """Initialize vision analyzer.

        Args:
            openrouter_client: OpenRouter API client
        """
        self.client = openrouter_client

    async def analyze_whiteboard(
        self,
        image: Image.Image,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Analyze whiteboard image.

        Args:
            image: PIL Image of the whiteboard
            context: Optional context from previous analysis

        Returns:
            Analysis result with structured information
        """
        prompt = """Analyze this whiteboard image. Describe:
1. What problem or topic is being worked on
2. What mathematical expressions, diagrams, or text are visible
3. What progress has been made
4. Any errors or issues you notice
5. The overall state of the work (just starting, in progress, nearly complete, etc.)

Be concise but thorough."""

        context_str = None
        if context:
            context_str = f"Previous analysis: {context.get('summary', '')}"

        try:
            analysis_text = await self.client.vision(
                image=image,
                prompt=prompt,
                context=context_str,
            )

            # Return structured analysis
            return {
                "raw_analysis": analysis_text,
                "has_content": len(analysis_text.strip()) > 0,
                "timestamp": None,  # Will be set by caller
            }

        except Exception as e:
            logger.error(f"Vision analysis error: {e}")
            return {
                "raw_analysis": "",
                "has_content": False,
                "error": str(e),
            }

    async def detect_changes(
        self,
        prev_image: Optional[Image.Image],
        curr_image: Image.Image,
        threshold: float = 0.1,
    ) -> bool:
        """Detect if significant changes occurred between images.

        Args:
            prev_image: Previous image (None if first frame)
            curr_image: Current image
            threshold: Threshold for significant change (0.0 to 1.0)

        Returns:
            True if significant change detected
        """
        if prev_image is None:
            return True

        try:
            # Simple pixel difference check
            # For MVP, just check if images are different enough
            # More sophisticated change detection can be added later

            # Resize to same size for comparison
            prev_resized = prev_image.resize((100, 100))
            curr_resized = curr_image.resize((100, 100))

            # Convert to grayscale
            prev_gray = prev_resized.convert("L")
            curr_gray = curr_resized.convert("L")

            # Calculate average pixel difference
            prev_array = np.array(prev_gray)
            curr_array = np.array(curr_gray)

            diff = np.abs(prev_array.astype(float) - curr_array.astype(float))
            avg_diff = np.mean(diff) / 255.0  # Normalize to 0-1

            return avg_diff > threshold

        except Exception as e:
            logger.error(f"Change detection error: {e}")
            return True  # Assume change on error to be safe
