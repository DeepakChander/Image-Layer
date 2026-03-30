from layer_ai.renderers.base import RendererNotImplementedError


class _StubRendererAdapter:
    def __init__(self, name: str) -> None:
        self.name = name

    def handoff(self, job_id: str, manifest: dict) -> dict:
        raise RendererNotImplementedError("Renderer adapter not implemented")


def get_renderer_adapter(renderer_name: str) -> _StubRendererAdapter:
    return _StubRendererAdapter(renderer_name)

