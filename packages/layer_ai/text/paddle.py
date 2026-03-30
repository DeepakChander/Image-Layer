from __future__ import annotations

from collections.abc import Iterable

from PIL.Image import Image

from layer_ai.text.models import TextCandidate


class PaddleOCRTextExtractor:
    def __init__(self) -> None:
        try:
            from paddleocr import PaddleOCR
        except ImportError as error:  # pragma: no cover - exercised when optional dependency is installed
            raise ImportError(
                "PaddleOCR is not installed. Install the optional 'ocr' dependency group."
            ) from error

        self._ocr = PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            enable_mkldnn=False,
        )

    def extract(self, image_path: str, image: Image) -> list[TextCandidate]:
        results = self._ocr.predict(input=image_path)
        return self._normalize_results(results)

    def _normalize_results(self, results: Iterable[object]) -> list[TextCandidate]:
        candidates: list[TextCandidate] = []
        for result in results:
            rec_texts = list(self._coerce_sequence(self._read_attr(result, "rec_texts")))
            rec_scores = list(self._coerce_sequence(self._read_attr(result, "rec_scores")))
            rec_boxes = self._first_non_empty_sequence(
                self._read_attr(result, "dt_polys"),
                self._read_attr(result, "rec_polys"),
                self._read_attr(result, "rec_boxes"),
                self._read_attr(result, "boxes"),
            )

            for index, text in enumerate(rec_texts):
                polygon = self._coerce_polygon(rec_boxes[index] if index < len(rec_boxes) else [])
                bbox = self._polygon_to_bbox(polygon)
                candidates.append(
                    TextCandidate(
                        text=str(text),
                        confidence=float(rec_scores[index] if index < len(rec_scores) else 0.0),
                        bbox=bbox,
                        polygon=polygon,
                    )
                )
        return candidates

    @staticmethod
    def _read_attr(result: object, attr: str):
        if hasattr(result, attr):
            return getattr(result, attr)
        if isinstance(result, dict):
            return result.get(attr)
        return None

    @staticmethod
    def _coerce_sequence(value: object) -> list:
        if value is None:
            return []
        if hasattr(value, "tolist"):
            coerced = value.tolist()
            return coerced if isinstance(coerced, list) else [coerced]
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        return [value]

    @staticmethod
    def _first_non_empty_sequence(*values: object) -> list:
        for value in values:
            sequence = PaddleOCRTextExtractor._coerce_sequence(value)
            if sequence:
                return sequence
        return []

    @staticmethod
    def _coerce_polygon(raw_polygon: object) -> list[tuple[int, int]]:
        polygon: list[tuple[int, int]] = []
        if not isinstance(raw_polygon, Iterable):
            return polygon
        for point in raw_polygon:
            if not isinstance(point, Iterable):
                continue
            values = list(point)
            if len(values) >= 2:
                polygon.append((int(values[0]), int(values[1])))
        return polygon

    @staticmethod
    def _polygon_to_bbox(polygon: list[tuple[int, int]]):
        from layer_ai.contracts.models import BoundingBox

        if not polygon:
            return BoundingBox(x=0, y=0, width=1, height=1)
        xs = [point[0] for point in polygon]
        ys = [point[1] for point in polygon]
        return BoundingBox(
            x=max(min(xs), 0),
            y=max(min(ys), 0),
            width=max(max(xs) - min(xs), 1),
            height=max(max(ys) - min(ys), 1),
        )
