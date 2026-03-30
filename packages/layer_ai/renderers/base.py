from typing import Protocol


class RendererNotImplementedError(NotImplementedError):
    """Raised when a renderer contract exists but no adapter is implemented yet."""


class RendererAdapter(Protocol):
    name: str

    def handoff(self, job_id: str, manifest: dict) -> dict:
        """Trigger handoff for a completed package."""

