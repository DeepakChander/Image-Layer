import json
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from PIL import Image, UnidentifiedImageError

from layer_ai.contracts.examples import build_example_scene_graph
from layer_ai.contracts.models import JobRecord, SceneManifest
from layer_ai.errors import InvalidImageError


class LocalArtifactStore:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def next_job_id(self) -> str:
        existing = sorted(self.root.glob("job_*"))
        return f"job_{len(existing) + 1:06d}"

    def write_job_record(self, record: JobRecord) -> None:
        job_root = self.job_root(record.job_id)
        job_root.mkdir(parents=True, exist_ok=True)
        (job_root / "job.json").write_text(record.model_dump_json(indent=2), encoding="utf-8")

    def read_job_record(self, job_id: str) -> JobRecord | None:
        path = self.job_root(job_id) / "job.json"
        if not path.exists():
            return None
        return JobRecord.model_validate_json(path.read_text(encoding="utf-8"))

    def write_manifest_pointer(self, job_id: str, manifest_path: Path) -> None:
        pointer = {"manifest_path": str(manifest_path)}
        (self.job_root(job_id) / "manifest-pointer.json").write_text(
            json.dumps(pointer, indent=2),
            encoding="utf-8",
        )

    def read_manifest(self, job_id: str) -> dict | None:
        pointer_path = self.job_root(job_id) / "manifest-pointer.json"
        if not pointer_path.exists():
            return None
        pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
        manifest_path = Path(pointer["manifest_path"])
        if not manifest_path.exists():
            return None
        return json.loads(manifest_path.read_text(encoding="utf-8"))

    def job_root(self, job_id: str) -> Path:
        return self.root / job_id

    def build_stub_package(self, job_id: str, image_bytes: bytes, filename: str) -> tuple[Path, Path]:
        job_root = self.job_root(job_id)
        input_dir = job_root / "input"
        cropped_dir = job_root / "layers" / "cropped"
        full_canvas_dir = job_root / "layers" / "full_canvas"
        masks_dir = job_root / "layers" / "masks"
        manifest_dir = job_root / "manifest"
        preview_dir = job_root / "preview"
        logs_dir = job_root / "logs"

        for directory in (
            input_dir,
            cropped_dir,
            full_canvas_dir,
            masks_dir,
            manifest_dir,
            preview_dir,
            logs_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)

        try:
            image = Image.open(BytesIO(image_bytes)).convert("RGBA")
        except UnidentifiedImageError as error:
            raise InvalidImageError("Uploaded bytes are not a valid image") from error
        safe_name = Path(filename).stem or "input"

        original_path = input_dir / "original.png"
        normalized_path = input_dir / "normalized.png"
        image.save(original_path)
        image.save(normalized_path)

        width, height = image.size
        layer_name = "layer_001_background"
        cropped_path = cropped_dir / f"{layer_name}.png"
        full_canvas_path = full_canvas_dir / f"{layer_name}.png"
        mask_path = masks_dir / f"{layer_name}_mask.png"
        reconstructed_path = preview_dir / "reconstructed.png"
        overlay_path = preview_dir / "overlay_debug.png"

        image.save(cropped_path)
        image.save(full_canvas_path)
        Image.new("L", image.size, color=255).save(mask_path)
        image.save(reconstructed_path)
        image.save(overlay_path)

        manifest = SceneManifest.model_validate(
            {
                "package_version": "1.0.0",
                "schema_version": "1.0.0",
                "job_id": job_id,
                "route": "design_route",
                "status": "completed_high_confidence",
                "global_confidence": 1.0,
                "warnings": [],
                "canvas": {"width": width, "height": height},
                "layers": [
                    {
                        "id": layer_name,
                        "name": f"{safe_name} background",
                        "type": "background",
                        "bbox": {"x": 0, "y": 0, "width": width, "height": height},
                        "z_index": 0,
                        "parent_id": None,
                        "cropped_asset": "layers/cropped/layer_001_background.png",
                        "full_canvas_asset": "layers/full_canvas/layer_001_background.png",
                        "mask_asset": "layers/masks/layer_001_background_mask.png",
                        "confidence": 1.0,
                        "warnings": [],
                        "editable_text": None,
                    }
                ],
            }
        )

        manifest_path = manifest_dir / "manifest.json"
        scene_graph_path = manifest_dir / "scene_graph.json"
        report_path = logs_dir / "job_report.json"
        confidence_path = logs_dir / "confidence_report.json"

        manifest_path.write_text(json.dumps(manifest.model_dump(mode="json"), indent=2), encoding="utf-8")
        scene_graph = build_example_scene_graph() | {"job_id": job_id}
        scene_graph_path.write_text(json.dumps(scene_graph, indent=2), encoding="utf-8")
        report_path.write_text(
            json.dumps(
                {
                    "job_id": job_id,
                    "status": "completed_high_confidence",
                    "route": "design_route",
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        confidence_path.write_text(
            json.dumps(
                {
                    "job_id": job_id,
                    "global_confidence": 1.0,
                    "layers": [{"id": layer_name, "confidence": 1.0}],
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        archive_path = job_root / f"{job_id}.zip"
        with ZipFile(archive_path, "w", compression=ZIP_DEFLATED) as archive:
            for file_path in job_root.rglob("*"):
                if file_path == archive_path or file_path.is_dir() or file_path.name in {
                    "job.json",
                    "manifest-pointer.json",
                }:
                    continue
                archive.write(file_path, arcname=file_path.relative_to(job_root).as_posix())

        return manifest_path, archive_path
