from PIL import Image, ImageDraw

from layer_ai.background.cleanup import BackgroundCleaner
from layer_ai.contracts.models import BoundingBox


def _image_with_block() -> Image.Image:
    image = Image.new("RGBA", (120, 80), color=(255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle((30, 20, 70, 50), fill=(20, 120, 220, 255))
    return image


def test_background_cleanup_fills_removed_region_deterministically():
    cleaner = BackgroundCleaner()
    image = _image_with_block()
    removal = BoundingBox(x=30, y=20, width=41, height=31)

    result = cleaner.clean(image, removals=[removal])

    assert result.image.size == image.size
    assert result.image.crop((30, 20, 71, 51)).tobytes() != image.crop((30, 20, 71, 51)).tobytes()


def test_background_cleanup_preserves_canvas_size():
    cleaner = BackgroundCleaner()
    image = _image_with_block()

    result = cleaner.clean(image, removals=[BoundingBox(x=30, y=20, width=41, height=31)])

    assert result.image.size == (120, 80)


def test_background_cleanup_warns_when_removed_area_is_large():
    cleaner = BackgroundCleaner()
    image = _image_with_block()

    result = cleaner.clean(
        image,
        removals=[
            BoundingBox(x=10, y=10, width=80, height=50),
        ],
    )

    assert "background_cleanup_approximate" in result.warnings
