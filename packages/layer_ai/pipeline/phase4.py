from __future__ import annotations

from dataclasses import dataclass

from PIL.Image import Image

from layer_ai.background.cleanup import BackgroundCleaner
from layer_ai.contracts.models import BoundingBox
from layer_ai.fusion.engine import FusionEngine
from layer_ai.preview.scoring import PreviewScorer, PreviewScore
from layer_ai.quality.evaluator import QualityEvaluator, QualityResult


@dataclass
class Phase4Artifacts:
    layers: list[dict]
    background_image: Image
    reconstructed_image: Image
    preview_score: PreviewScore
    quality: QualityResult


class Phase4Pipeline:
    MIN_VISUAL_EFFECT_RATIO = 0.005
    MIN_VISUAL_FOREGROUND_RATIO = 0.1
    NOOP_VISUAL_RECONSTRUCTION_CAP = 0.5

    def __init__(
        self,
        fusion_engine: FusionEngine | None = None,
        background_cleaner: BackgroundCleaner | None = None,
        preview_scorer: PreviewScorer | None = None,
        quality_evaluator: QualityEvaluator | None = None,
    ) -> None:
        self.fusion_engine = fusion_engine or FusionEngine()
        self.background_cleaner = background_cleaner or BackgroundCleaner()
        self.preview_scorer = preview_scorer or PreviewScorer()
        self.quality_evaluator = quality_evaluator or QualityEvaluator()

    def run(
        self,
        original_image: Image,
        text_layers: list[dict],
        visual_layers: list[dict],
    ) -> Phase4Artifacts:
        fused = self.fusion_engine.fuse(text_layers=text_layers, visual_layers=visual_layers)
        removals = [BoundingBox.model_validate(layer["bbox"]) for layer in fused.layers]
        background = self.background_cleaner.clean(original_image, removals=removals)
        background_effect = self.preview_scorer.score(original_image, background.image)

        reconstructed = background.image.copy()
        for layer in fused.layers:
            reconstructed.alpha_composite(layer["full_canvas_image"])

        preview_score = self.preview_scorer.score(original_image, reconstructed)
        has_visual_layers = any(layer["type"] != "text" for layer in fused.layers)
        visual_foreground_ratios = [
            self._measure_foreground_ratio(original_image, layer["cropped_image"])
            for layer in fused.layers
            if layer["type"] != "text"
        ]
        has_low_content_visual = bool(visual_foreground_ratios) and min(visual_foreground_ratios) < self.MIN_VISUAL_FOREGROUND_RATIO
        if has_visual_layers and (
            background_effect.preview_diff_ratio < self.MIN_VISUAL_EFFECT_RATIO
            or has_low_content_visual
        ):
            preview_score = PreviewScore(
                reconstruction_score=min(
                    preview_score.reconstruction_score,
                    self.NOOP_VISUAL_RECONSTRUCTION_CAP,
                ),
                preview_diff_ratio=preview_score.preview_diff_ratio,
                changed_pixels=preview_score.changed_pixels,
            )
        quality = self.quality_evaluator.evaluate(
            text_confidences=[layer["confidence"] for layer in fused.layers if layer["type"] == "text"],
            visual_confidences=[layer["confidence"] for layer in fused.layers if layer["type"] != "text"],
            reconstruction_score=preview_score.reconstruction_score,
            warnings=[*fused.warnings, *background.warnings],
        )

        return Phase4Artifacts(
            layers=fused.layers,
            background_image=background.image,
            reconstructed_image=reconstructed,
            preview_score=preview_score,
            quality=quality,
        )

    @staticmethod
    def _measure_foreground_ratio(original_image: Image, cropped_image: Image) -> float:
        background_color = Phase4Pipeline._estimate_canvas_background(original_image)
        visible_pixels = 0
        foreground_pixels = 0

        for red, green, blue, alpha in cropped_image.convert("RGBA").getdata():
            if alpha <= 0:
                continue
            visible_pixels += 1
            if max(
                abs(red - background_color[0]),
                abs(green - background_color[1]),
                abs(blue - background_color[2]),
            ) > 20:
                foreground_pixels += 1

        if visible_pixels == 0:
            return 0.0
        return foreground_pixels / visible_pixels

    @staticmethod
    def _estimate_canvas_background(image: Image) -> tuple[int, int, int]:
        rgba = image.convert("RGBA")
        width, height = rgba.size
        corners = [
            rgba.getpixel((0, 0)),
            rgba.getpixel((max(width - 1, 0), 0)),
            rgba.getpixel((0, max(height - 1, 0))),
            rgba.getpixel((max(width - 1, 0), max(height - 1, 0))),
        ]
        return tuple(int(sum(pixel[channel] for pixel in corners) / len(corners)) for channel in range(3))
