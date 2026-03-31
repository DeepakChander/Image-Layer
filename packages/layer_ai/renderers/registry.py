from layer_ai.renderers.after_effects import AfterEffectsRendererAdapter
from layer_ai.renderers.base import RendererAdapter, UnsupportedRendererError
from layer_ai.renderers.remotion import RemotionRendererAdapter


def get_renderer_adapter(renderer_name: str) -> RendererAdapter:
    adapters: dict[str, RendererAdapter] = {
        "after-effects": AfterEffectsRendererAdapter(),
        "remotion": RemotionRendererAdapter(),
    }
    try:
        return adapters[renderer_name]
    except KeyError as error:
        raise UnsupportedRendererError(f"Unsupported renderer: {renderer_name}") from error
