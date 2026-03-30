import logging

from layer_ai.config import Settings
from layer_ai.text.noop import NoopTextExtractor
from layer_ai.text.paddle import PaddleOCRTextExtractor

logger = logging.getLogger(__name__)


def build_text_extractor(settings: Settings):
    backend = settings.ocr_backend.lower()
    if backend == "disabled":
        return NoopTextExtractor()
    if backend == "paddle":
        return PaddleOCRTextExtractor()
    if backend == "auto":
        try:
            return PaddleOCRTextExtractor()
        except ImportError:
            return NoopTextExtractor()
        except Exception:  # pragma: no cover - exercised with monkeypatch in tests
            logger.warning("Falling back to NoopTextExtractor after PaddleOCR auto-init failure", exc_info=True)
            return NoopTextExtractor()
    return NoopTextExtractor()
