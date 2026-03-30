from PIL.Image import Image

from layer_ai.text.models import TextCandidate


class NoopTextExtractor:
    def extract(self, image_path: str, image: Image) -> list[TextCandidate]:
        return []

