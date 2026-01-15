"""Image preprocessing for vision analysis."""

import logging
from PIL import Image, ImageEnhance, ImageFilter
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """Preprocesses images for optimal LLM analysis."""

    def __init__(
        self,
        target_size: Tuple[int, int] = (1024, 768),
        enhance_contrast: bool = True,
        sharpen: bool = True,
    ):
        """Initialize image preprocessor.

        Args:
            target_size: Target size for resized images
            enhance_contrast: Whether to enhance contrast
            sharpen: Whether to sharpen the image
        """
        self.target_size = target_size
        self.enhance_contrast = enhance_contrast
        self.sharpen = sharpen

    def preprocess(self, image: Image.Image) -> Image.Image:
        """Preprocess an image.

        Args:
            image: Input PIL Image

        Returns:
            Preprocessed PIL Image
        """
        try:
            # Convert to RGB if needed
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Resize while maintaining aspect ratio
            image = self._resize_maintain_aspect(image)

            # Enhance contrast
            if self.enhance_contrast:
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(1.5)

            # Sharpen
            if self.sharpen:
                image = image.filter(ImageFilter.SHARPEN)

            return image

        except Exception as e:
            logger.error(f"Image preprocessing error: {e}")
            return image  # Return original on error

    def _resize_maintain_aspect(self, image: Image.Image) -> Image.Image:
        """Resize image while maintaining aspect ratio.

        Args:
            image: Input PIL Image

        Returns:
            Resized PIL Image
        """
        # Calculate aspect ratio
        aspect = image.width / image.height
        target_aspect = self.target_size[0] / self.target_size[1]

        if aspect > target_aspect:
            # Image is wider
            new_width = self.target_size[0]
            new_height = int(new_width / aspect)
        else:
            # Image is taller
            new_height = self.target_size[1]
            new_width = int(new_height * aspect)

        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    def crop_to_whiteboard(
        self,
        image: Image.Image,
        crop_box: Optional[Tuple[int, int, int, int]] = None,
    ) -> Image.Image:
        """Crop image to whiteboard region.

        Args:
            image: Input PIL Image
            crop_box: Optional (left, top, right, bottom) crop coordinates

        Returns:
            Cropped PIL Image
        """
        if crop_box:
            try:
                return image.crop(crop_box)
            except Exception as e:
                logger.error(f"Crop error: {e}")
                return image
        return image
