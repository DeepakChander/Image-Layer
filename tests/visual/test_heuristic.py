from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from layer_ai.text.models import TextCandidate
from layer_ai.visual.heuristic import HeuristicVisualExtractor


def _shape_image():
    image = Image.new("RGB", (240, 120), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((32, 28, 108, 72), fill=(27, 99, 198), radius=8)
    return image.convert("RGBA")


def _text_only_image():
    image = Image.new("RGB", (240, 120), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.text((24, 36), "HELLO", fill=(0, 0, 0), font=ImageFont.load_default())
    return image.convert("RGBA")


def test_heuristic_visual_extractor_detects_non_text_block():
    extractor = HeuristicVisualExtractor()

    candidates = extractor.extract(_shape_image(), [])

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.layer_type in {"shape", "button"}
    assert candidate.bbox.x <= 32
    assert candidate.bbox.y <= 28
    assert candidate.bbox.width >= 76
    assert candidate.bbox.height >= 44


def test_heuristic_visual_extractor_ignores_masked_text_regions():
    extractor = HeuristicVisualExtractor()
    text_candidate = TextCandidate(
        text="HELLO",
        confidence=0.99,
        bbox={"x": 24, "y": 36, "width": 40, "height": 10},
        polygon=[(24, 36), (64, 36), (64, 46), (24, 46)],
    )

    candidates = extractor.extract(_text_only_image(), [text_candidate])

    assert candidates == []
