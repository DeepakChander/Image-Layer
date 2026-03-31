from __future__ import annotations

from dataclasses import dataclass, field

from PIL import Image, ImageFilter

from layer_ai.contracts.models import BoundingBox


@dataclass
class BackgroundCleanupResult:
    image: Image.Image
    warnings: list[str] = field(default_factory=list)


class BackgroundCleaner:
    APPROXIMATE_COVERAGE_THRESHOLD = 0.35

    def clean(self, image: Image.Image, removals: list[BoundingBox]) -> BackgroundCleanupResult:
        cleaned = image.convert("RGBA").copy()
        total_area = cleaned.size[0] * cleaned.size[1]
        removed_area = 0

        for removal in removals:
            removed_area += removal.width * removal.height
            fill_color = self._estimate_surrounding_color(cleaned, removal)
            region = Image.new("RGBA", (removal.width, removal.height), color=fill_color)
            region = region.filter(ImageFilter.BoxBlur(1))
            cleaned.paste(region, (removal.x, removal.y))

        warnings: list[str] = []
        if total_area > 0 and (removed_area / total_area) >= self.APPROXIMATE_COVERAGE_THRESHOLD:
            warnings.append("background_cleanup_approximate")
        return BackgroundCleanupResult(image=cleaned, warnings=warnings)

    @staticmethod
    def _estimate_surrounding_color(image: Image.Image, removal: BoundingBox) -> tuple[int, int, int, int]:
        pixels: list[tuple[int, int, int, int]] = []
        width, height = image.size
        left = max(removal.x - 1, 0)
        right = min(removal.x + removal.width, width - 1)
        top = max(removal.y - 1, 0)
        bottom = min(removal.y + removal.height, height - 1)

        for x in range(removal.x, min(removal.x + removal.width, width)):
            pixels.append(image.getpixel((x, top)))
            pixels.append(image.getpixel((x, bottom)))
        for y in range(removal.y, min(removal.y + removal.height, height)):
            pixels.append(image.getpixel((left, y)))
            pixels.append(image.getpixel((right, y)))

        if not pixels:
            return (255, 255, 255, 255)

        return tuple(int(sum(pixel[channel] for pixel in pixels) / len(pixels)) for channel in range(4))
