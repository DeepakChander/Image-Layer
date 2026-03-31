from PIL import Image, ImageDraw

from layer_ai.preview.scoring import PreviewScorer


def test_preview_scoring_returns_perfect_score_for_identical_images():
    scorer = PreviewScorer()
    original = Image.new("RGBA", (40, 30), color=(255, 255, 255, 255))

    result = scorer.score(original, original.copy())

    assert result.reconstruction_score == 1.0
    assert result.preview_diff_ratio == 0.0
    assert result.changed_pixels == 0


def test_preview_scoring_drops_for_changed_pixels():
    scorer = PreviewScorer()
    original = Image.new("RGBA", (40, 30), color=(255, 255, 255, 255))
    reconstructed = original.copy()
    ImageDraw.Draw(reconstructed).rectangle((10, 10, 20, 20), fill=(0, 0, 0, 255))

    result = scorer.score(original, reconstructed)

    assert result.reconstruction_score < 1.0
    assert result.preview_diff_ratio > 0.0
    assert result.changed_pixels > 0
