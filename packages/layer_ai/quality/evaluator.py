from __future__ import annotations

from dataclasses import dataclass


@dataclass
class QualityResult:
    status: str
    global_confidence: float
    warnings: list[str]


class QualityEvaluator:
    HIGH_CONFIDENCE_THRESHOLD = 0.9
    LOW_CONFIDENCE_THRESHOLD = 0.6
    RECONSTRUCTION_WARNING_THRESHOLD = 0.9
    RECONSTRUCTION_LOW_THRESHOLD = 0.75
    DUPLICATE_PENALTY = 0.05
    BACKGROUND_PENALTY = 0.05

    def evaluate(
        self,
        text_confidences: list[float],
        visual_confidences: list[float],
        reconstruction_score: float,
        warnings: list[str],
    ) -> QualityResult:
        final_warnings = list(dict.fromkeys(warnings))

        if text_confidences and min(text_confidences) < self.HIGH_CONFIDENCE_THRESHOLD and "low_text_confidence" not in final_warnings:
            final_warnings.append("low_text_confidence")
        if visual_confidences and min(visual_confidences) < self.HIGH_CONFIDENCE_THRESHOLD and "low_visual_confidence" not in final_warnings:
            final_warnings.append("low_visual_confidence")
        if reconstruction_score < self.RECONSTRUCTION_WARNING_THRESHOLD and "reconstruction_mismatch" not in final_warnings:
            final_warnings.append("reconstruction_mismatch")

        evidence = [*text_confidences, *visual_confidences, reconstruction_score]
        global_confidence = min(evidence) if evidence else 1.0

        if "possible_duplicate_layers" in final_warnings:
            global_confidence -= self.DUPLICATE_PENALTY
        if "background_cleanup_approximate" in final_warnings:
            global_confidence -= self.BACKGROUND_PENALTY

        global_confidence = round(min(max(global_confidence, 0.0), 1.0), 6)

        if global_confidence < self.LOW_CONFIDENCE_THRESHOLD or reconstruction_score < self.RECONSTRUCTION_LOW_THRESHOLD:
            status = "completed_low_confidence"
        elif final_warnings:
            status = "completed_with_warnings"
        else:
            status = "completed_high_confidence"

        return QualityResult(
            status=status,
            global_confidence=global_confidence,
            warnings=final_warnings,
        )
