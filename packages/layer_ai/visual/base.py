from typing import Protocol

from PIL.Image import Image

from layer_ai.text.models import TextCandidate
from layer_ai.visual.models import VisualCandidate


class VisualExtractor(Protocol):
    def extract(self, image: Image, text_candidates: list[TextCandidate]) -> list[VisualCandidate]:
        """Return non-text visual candidates for a single image."""
