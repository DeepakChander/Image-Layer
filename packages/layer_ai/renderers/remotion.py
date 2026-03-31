from datetime import UTC, datetime
from pathlib import Path

from layer_ai.renderers.base import RendererAdapter
from layer_ai.renderers.models import RendererHandoff, RendererHandoffResult, RendererLayerRef
from layer_ai.storage.local import LocalArtifactStore


class RemotionRendererAdapter(RendererAdapter):
    name = "remotion"

    def handoff(self, job_id: str, job_root: Path, manifest: dict) -> RendererHandoffResult:
        ordered_layers = sorted(manifest["layers"], key=lambda layer: layer["z_index"])
        layer_refs = [
            RendererLayerRef.model_validate(
                {
                    "id": layer["id"],
                    "name": layer["name"],
                    "type": layer["type"],
                    "z_index": layer["z_index"],
                    "bbox": layer["bbox"],
                    "cropped_asset_path": LocalArtifactStore.resolve_job_asset_path(job_root, layer["cropped_asset"]),
                    "full_canvas_asset_path": LocalArtifactStore.resolve_job_asset_path(job_root, layer["full_canvas_asset"]),
                    "mask_asset_path": LocalArtifactStore.resolve_job_asset_path(job_root, layer["mask_asset"]),
                    "confidence": layer["confidence"],
                    "warnings": layer.get("warnings", []),
                    "text_content": layer.get("text_content"),
                    "text_confidence": layer.get("text_confidence"),
                    "editable_text": layer.get("editable_text"),
                }
            )
            for layer in ordered_layers
        ]

        background_layer = next(layer for layer in layer_refs if layer.type == "background")
        handoff = RendererHandoff(
            job_id=job_id,
            renderer=self.name,
            created_at=datetime.now(UTC).isoformat(),
            manifest_path=LocalArtifactStore.resolve_job_asset_path(job_root, "manifest/manifest.json"),
            original_image_path=LocalArtifactStore.resolve_job_asset_path(job_root, "input/original.png"),
            background_asset_path=background_layer.full_canvas_asset_path,
            global_confidence=manifest["global_confidence"],
            reconstruction_score=manifest.get("reconstruction_score"),
            warnings=manifest.get("warnings", []),
            layers=layer_refs,
        )

        handoff_path = LocalArtifactStore.renderer_handoff_path(job_root, self.name)
        LocalArtifactStore.write_renderer_handoff(handoff_path, handoff)
        return RendererHandoffResult(
            job_id=job_id,
            renderer=self.name,
            handoff_path=handoff_path.relative_to(job_root).as_posix(),
            layer_count=len(layer_refs),
        )
