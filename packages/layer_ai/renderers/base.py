from pathlib import Path
from typing import Protocol

from layer_ai.renderers.models import RendererHandoffResult


class RendererNotImplementedError(NotImplementedError):
    """Raised when a renderer contract exists but no adapter is implemented yet."""


class RendererAdapter(Protocol):
    name: str

    def handoff(self, job_id: str, job_root: Path, manifest: dict) -> RendererHandoffResult:
        """Trigger handoff for a completed package."""
