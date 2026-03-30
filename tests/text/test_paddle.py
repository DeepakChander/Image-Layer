import numpy as np

from layer_ai.config import Settings
from layer_ai.text.factory import build_text_extractor
from layer_ai.text.noop import NoopTextExtractor
from layer_ai.text.paddle import PaddleOCRTextExtractor


class _FakeResult:
    rec_texts = ["HELLO"]
    rec_scores = [0.98]
    dt_polys = [[[10, 20], [40, 20], [40, 34], [10, 34]]]


def test_paddle_text_extractor_normalizes_prediction_results_without_runtime():
    extractor = PaddleOCRTextExtractor.__new__(PaddleOCRTextExtractor)

    candidates = extractor._normalize_results([_FakeResult()])

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.text == "HELLO"
    assert candidate.confidence == 0.98
    assert candidate.bbox.x == 10
    assert candidate.bbox.y == 20
    assert candidate.bbox.width == 30
    assert candidate.bbox.height == 14


def test_paddle_text_extractor_handles_empty_numpy_box_arrays():
    extractor = PaddleOCRTextExtractor.__new__(PaddleOCRTextExtractor)

    candidates = extractor._normalize_results(
        [
            {
                "rec_texts": [],
                "rec_scores": [],
                "rec_boxes": np.array([]),
                "rec_polys": [],
            }
        ]
    )

    assert candidates == []


def test_build_text_extractor_auto_falls_back_to_noop_when_runtime_init_fails(monkeypatch):
    def raising_extractor():  # noqa: ANN202
        raise RuntimeError("Paddle runtime unavailable")

    monkeypatch.setattr("layer_ai.text.factory.PaddleOCRTextExtractor", raising_extractor)

    extractor = build_text_extractor(Settings(ocr_backend="auto"))

    assert isinstance(extractor, NoopTextExtractor)
