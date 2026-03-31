from __future__ import annotations

from layer_ai.fusion.models import FusionResult


class FusionEngine:
    TEXT_VISUAL_IOU_THRESHOLD = 0.5
    VISUAL_DUPLICATE_IOU_THRESHOLD = 0.8

    def fuse(self, text_layers: list[dict], visual_layers: list[dict]) -> FusionResult:
        warnings: list[str] = []
        surviving_visuals = self._remove_visual_duplicates(visual_layers, warnings)
        filtered_visuals = [
            layer
            for layer in surviving_visuals
            if not any(self._iou(layer["bbox"], text_layer["bbox"]) >= self.TEXT_VISUAL_IOU_THRESHOLD for text_layer in text_layers)
        ]
        layers = sorted(
            [*filtered_visuals, *text_layers],
            key=lambda layer: (layer["z_index"], layer["id"]),
        )
        return FusionResult(layers=layers, warnings=warnings)

    def _remove_visual_duplicates(self, visual_layers: list[dict], warnings: list[str]) -> list[dict]:
        survivors: list[dict] = []
        for layer in sorted(visual_layers, key=lambda item: (-item["confidence"], item["id"])):
            duplicate_index = next(
                (
                    index
                    for index, survivor in enumerate(survivors)
                    if survivor["type"] == layer["type"]
                    and self._iou(survivor["bbox"], layer["bbox"]) >= self.VISUAL_DUPLICATE_IOU_THRESHOLD
                ),
                None,
            )
            if duplicate_index is not None:
                if "possible_duplicate_layers" not in warnings:
                    warnings.append("possible_duplicate_layers")
                continue
            survivors.append(layer)
        return survivors

    @staticmethod
    def _iou(first: dict, second: dict) -> float:
        first_x2 = first["x"] + first["width"]
        first_y2 = first["y"] + first["height"]
        second_x2 = second["x"] + second["width"]
        second_y2 = second["y"] + second["height"]

        intersection_left = max(first["x"], second["x"])
        intersection_top = max(first["y"], second["y"])
        intersection_right = min(first_x2, second_x2)
        intersection_bottom = min(first_y2, second_y2)

        if intersection_right <= intersection_left or intersection_bottom <= intersection_top:
            return 0.0

        intersection_area = (intersection_right - intersection_left) * (intersection_bottom - intersection_top)
        first_area = first["width"] * first["height"]
        second_area = second["width"] * second["height"]
        union_area = first_area + second_area - intersection_area
        if union_area <= 0:
            return 0.0
        return intersection_area / union_area
