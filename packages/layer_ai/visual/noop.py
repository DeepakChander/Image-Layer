from PIL.Image import Image

from layer_ai.text.models import TextCandidate
from layer_ai.visual.models import VisualCandidate


class NoopVisualExtractor:
    def extract(self, image: Image, text_candidates: list[TextCandidate]) -> list[VisualCandidate]:
        return []
