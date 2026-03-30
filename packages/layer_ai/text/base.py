from typing import Protocol

from PIL.Image import Image

from layer_ai.text.models import TextCandidate


class TextExtractor(Protocol):
    def extract(self, image_path: str, image: Image) -> list[TextCandidate]:
        """Return OCR text candidates for a single image."""

