from __future__ import annotations

from dataclasses import dataclass

from PIL import Image, ImageChops


@dataclass
class PreviewScore:
    reconstruction_score: float
    preview_diff_ratio: float
    changed_pixels: int


class PreviewScorer:
    def score(self, original: Image.Image, reconstructed: Image.Image) -> PreviewScore:
        base = original.convert("RGBA")
        candidate = reconstructed.convert("RGBA")
        if candidate.size != base.size:
            candidate = candidate.resize(base.size)

        diff = ImageChops.difference(base, candidate)
        changed_pixels = sum(1 for pixel in diff.getdata() if any(channel != 0 for channel in pixel))
        total_pixels = base.size[0] * base.size[1]
        preview_diff_ratio = 0.0 if total_pixels == 0 else changed_pixels / total_pixels
        reconstruction_score = max(0.0, 1.0 - preview_diff_ratio)
        return PreviewScore(
            reconstruction_score=round(reconstruction_score, 6),
            preview_diff_ratio=round(preview_diff_ratio, 6),
            changed_pixels=changed_pixels,
        )
