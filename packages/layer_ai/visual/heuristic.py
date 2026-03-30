from __future__ import annotations

from collections import deque

from PIL import ImageChops
from PIL.Image import Image

from layer_ai.contracts.models import BoundingBox
from layer_ai.text.models import TextCandidate
from layer_ai.visual.models import VisualCandidate


class HeuristicVisualExtractor:
    def __init__(
        self,
        background_threshold: int = 20,
        min_area_pixels: int = 96,
    ) -> None:
        self.background_threshold = background_threshold
        self.min_area_pixels = min_area_pixels

    def extract(self, image: Image, text_candidates: list[TextCandidate]) -> list[VisualCandidate]:
        working_image = image.convert("RGBA").copy()
        background_color = self._estimate_background_color(working_image)
        self._mask_text_regions(working_image, text_candidates, background_color)
        difference = ImageChops.difference(
            working_image.convert("RGB"),
            self._solid_background(working_image.size, background_color),
        ).convert("L")
        binary_mask = difference.point(lambda value: 255 if value > self.background_threshold else 0)
        return self._connected_components(binary_mask)

    def _connected_components(self, binary_mask: Image) -> list[VisualCandidate]:
        width, height = binary_mask.size
        pixels = binary_mask.load()
        visited = bytearray(width * height)
        candidates: list[VisualCandidate] = []

        for y in range(height):
            for x in range(width):
                index = y * width + x
                if visited[index] or pixels[x, y] == 0:
                    continue

                queue: deque[tuple[int, int]] = deque([(x, y)])
                visited[index] = 1
                points: list[tuple[int, int]] = []
                min_x = max_x = x
                min_y = max_y = y

                while queue:
                    px, py = queue.popleft()
                    points.append((px, py))
                    min_x = min(min_x, px)
                    min_y = min(min_y, py)
                    max_x = max(max_x, px)
                    max_y = max(max_y, py)

                    for next_x, next_y in (
                        (px - 1, py),
                        (px + 1, py),
                        (px, py - 1),
                        (px, py + 1),
                    ):
                        if not (0 <= next_x < width and 0 <= next_y < height):
                            continue
                        next_index = next_y * width + next_x
                        if visited[next_index] or pixels[next_x, next_y] == 0:
                            continue
                        visited[next_index] = 1
                        queue.append((next_x, next_y))

                if len(points) < self.min_area_pixels:
                    continue

                bbox = BoundingBox(
                    x=min_x,
                    y=min_y,
                    width=(max_x - min_x) + 1,
                    height=(max_y - min_y) + 1,
                )
                mask = [[0 for _ in range(bbox.width)] for _ in range(bbox.height)]
                for point_x, point_y in points:
                    mask[point_y - min_y][point_x - min_x] = 255

                area = len(points)
                density = area / (bbox.width * bbox.height)
                layer_type = self._classify_layer_type(bbox, density, width, height)
                confidence = round(min(max(0.55, 0.45 + density), 0.95), 2)
                candidates.append(
                    VisualCandidate(
                        label=f"{layer_type}_{len(candidates) + 1}",
                        layer_type=layer_type,
                        confidence=confidence,
                        bbox=bbox,
                        mask=mask,
                    )
                )

        return candidates

    @staticmethod
    def _solid_background(size: tuple[int, int], color: tuple[int, int, int]) -> Image:
        from PIL import Image as PILImage

        return PILImage.new("RGB", size, color=color)

    @staticmethod
    def _mask_text_regions(
        image: Image,
        text_candidates: list[TextCandidate],
        background_color: tuple[int, int, int],
    ) -> None:
        for candidate in text_candidates:
            bbox = candidate.bbox
            image.paste((*background_color, 255), (bbox.x, bbox.y, bbox.x + bbox.width, bbox.y + bbox.height))

    @staticmethod
    def _estimate_background_color(image: Image) -> tuple[int, int, int]:
        rgb_image = image.convert("RGB")
        width, height = rgb_image.size
        pixels: list[tuple[int, int, int]] = []

        for x in range(width):
            pixels.append(rgb_image.getpixel((x, 0)))
            if height > 1:
                pixels.append(rgb_image.getpixel((x, height - 1)))
        for y in range(1, height - 1):
            pixels.append(rgb_image.getpixel((0, y)))
            if width > 1:
                pixels.append(rgb_image.getpixel((width - 1, y)))

        if not pixels:
            return (255, 255, 255)

        return tuple(int(sum(color[channel] for color in pixels) / len(pixels)) for channel in range(3))

    @staticmethod
    def _classify_layer_type(
        bbox: BoundingBox,
        density: float,
        image_width: int,
        image_height: int,
    ) -> str:
        area_ratio = (bbox.width * bbox.height) / max(image_width * image_height, 1)
        aspect_ratio = bbox.width / max(bbox.height, 1)
        if aspect_ratio >= 1.6 and area_ratio <= 0.2 and density >= 0.55:
            return "button"
        if area_ratio >= 0.15:
            return "image"
        return "shape"
