class InvalidImageError(ValueError):
    """Raised when uploaded bytes do not represent a valid image."""


class RendererJobNotReadyError(RuntimeError):
    """Raised when a job is not yet eligible for renderer handoff."""
