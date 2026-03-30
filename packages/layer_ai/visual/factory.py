from layer_ai.config import Settings
from layer_ai.visual.heuristic import HeuristicVisualExtractor
from layer_ai.visual.noop import NoopVisualExtractor


def build_visual_extractor(settings: Settings):
    backend = settings.visual_backend.lower()
    if backend == "disabled":
        return NoopVisualExtractor()
    if backend == "heuristic":
        return HeuristicVisualExtractor()
    return NoopVisualExtractor()
