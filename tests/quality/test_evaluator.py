from layer_ai.quality.evaluator import QualityEvaluator


def test_quality_adds_low_text_confidence_warning():
    evaluator = QualityEvaluator()

    result = evaluator.evaluate(
        text_confidences=[0.58],
        visual_confidences=[],
        reconstruction_score=0.98,
        warnings=[],
    )

    assert "low_text_confidence" in result.warnings
    assert result.status == "completed_low_confidence"


def test_quality_adds_low_visual_confidence_warning():
    evaluator = QualityEvaluator()

    result = evaluator.evaluate(
        text_confidences=[],
        visual_confidences=[0.72],
        reconstruction_score=0.98,
        warnings=[],
    )

    assert "low_visual_confidence" in result.warnings
    assert result.status == "completed_with_warnings"


def test_quality_marks_job_low_confidence_when_reconstruction_is_poor():
    evaluator = QualityEvaluator()

    result = evaluator.evaluate(
        text_confidences=[0.95],
        visual_confidences=[0.92],
        reconstruction_score=0.42,
        warnings=[],
    )

    assert result.status == "completed_low_confidence"
    assert "reconstruction_mismatch" in result.warnings


def test_quality_penalizes_duplicate_warning_in_global_confidence():
    evaluator = QualityEvaluator()

    result = evaluator.evaluate(
        text_confidences=[0.95],
        visual_confidences=[0.92],
        reconstruction_score=0.96,
        warnings=["possible_duplicate_layers"],
    )

    assert result.global_confidence < 0.92
    assert "possible_duplicate_layers" in result.warnings
