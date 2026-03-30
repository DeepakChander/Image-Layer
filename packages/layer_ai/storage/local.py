import json
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from PIL import Image, ImageChops, UnidentifiedImageError

from layer_ai.contracts.examples import build_scene_graph
from layer_ai.contracts.models import BoundingBox, EditableText, JobRecord, SceneManifest
from layer_ai.errors import InvalidImageError
from layer_ai.text.base import TextExtractor
from layer_ai.text.models import TextCandidate


class LocalArtifactStore:
    HIGH_CONFIDENCE_THRESHOLD = 0.9
    LOW_CONFIDENCE_THRESHOLD = 0.6

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

    def build_package(
        self,
        job_id: str,
        image_bytes: bytes,
        filename: str,
        text_extractor: TextExtractor,
        editable_text_confidence_threshold: float,
    ) -> tuple[SceneManifest, Path, Path]:
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
            raise InvalidImageError("Invalid image file") from error
        safe_name = Path(filename).stem or "input"

        original_path = input_dir / "original.png"
        normalized_path = input_dir / "normalized.png"
        image.save(original_path)
        image.save(normalized_path)

        width, height = image.size
        background_image = image.copy()
        reconstructed_image = background_image.copy()
        reconstructed_path = preview_dir / "reconstructed.png"
        overlay_path = preview_dir / "overlay_debug.png"

        layers: list[dict] = []

        layer_name = "layer_001_background"
        cropped_path = cropped_dir / f"{layer_name}.png"
        full_canvas_path = full_canvas_dir / f"{layer_name}.png"
        mask_path = masks_dir / f"{layer_name}_mask.png"
        layers.append(
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
                "text_content": None,
                "text_confidence": None,
                "editable_text": None,
            }
        )

        text_candidates = text_extractor.extract(str(normalized_path), image.copy())
        for index, candidate in enumerate(text_candidates, start=1):
            layer_index = len(layers) + 1
            layer_name = f"layer_{layer_index:03d}_text_{index:03d}"
            bbox = self._clamp_bbox(candidate.bbox, image.size)
            if bbox.width <= 0 or bbox.height <= 0:
                continue

            rgba_crop, alpha_mask = self._extract_text_rgba(image, bbox)
            text_cropped_path = cropped_dir / f"{layer_name}.png"
            text_full_canvas_path = full_canvas_dir / f"{layer_name}.png"
            text_mask_path = masks_dir / f"{layer_name}_mask.png"
            rgba_crop.save(text_cropped_path)

            full_canvas_image = Image.new("RGBA", image.size, color=(0, 0, 0, 0))
            full_canvas_image.paste(rgba_crop, (bbox.x, bbox.y), rgba_crop)
            full_canvas_image.save(text_full_canvas_path)
            alpha_mask.save(text_mask_path)
            background_patch = Image.new(
                "RGBA",
                rgba_crop.size,
                color=(*self._estimate_background_color(rgba_crop), 255),
            )
            background_image.paste(background_patch, (bbox.x, bbox.y), alpha_mask)
            reconstructed_image.paste(rgba_crop, (bbox.x, bbox.y), rgba_crop)

            editable_text = None
            if candidate.confidence >= editable_text_confidence_threshold:
                editable_text = EditableText(
                    text=candidate.text,
                    font_family_guess="Unknown",
                    font_weight=400,
                    font_size_px=max(bbox.height, 1),
                    fill=self._estimate_fill_hex(rgba_crop),
                    alignment="left",
                    confidence=candidate.confidence,
                )

            layer_warnings: list[str] = []
            if candidate.confidence < self.HIGH_CONFIDENCE_THRESHOLD:
                layer_warnings.append("low_text_confidence")

            layers.append(
                {
                    "id": layer_name,
                    "name": f"{candidate.text.lower()} text",
                    "type": "text",
                    "bbox": bbox.model_dump(mode="json"),
                    "z_index": layer_index - 1,
                    "parent_id": None,
                    "cropped_asset": f"layers/cropped/{layer_name}.png",
                    "full_canvas_asset": f"layers/full_canvas/{layer_name}.png",
                    "mask_asset": f"layers/masks/{layer_name}_mask.png",
                    "confidence": candidate.confidence,
                    "warnings": layer_warnings,
                    "text_content": candidate.text,
                    "text_confidence": candidate.confidence,
                    "editable_text": None if editable_text is None else editable_text.model_dump(mode="json"),
                }
            )

        background_image.save(cropped_path)
        background_image.save(full_canvas_path)
        Image.new("L", image.size, color=255).save(mask_path)
        reconstructed_image.save(reconstructed_path)
        self._build_overlay_debug(image, overlay_path, text_candidates)
        global_confidence = self._compute_global_confidence(layers)
        warnings = self._collect_manifest_warnings(layers)
        status = self._determine_status(global_confidence, warnings)

        manifest = SceneManifest.model_validate(
            {
                "package_version": "1.0.0",
                "schema_version": "1.0.0",
                "job_id": job_id,
                "route": "design_route",
                "status": status,
                "global_confidence": global_confidence,
                "warnings": warnings,
                "canvas": {"width": width, "height": height},
                "layers": layers,
            }
        )

        manifest_path = manifest_dir / "manifest.json"
        scene_graph_path = manifest_dir / "scene_graph.json"
        report_path = logs_dir / "job_report.json"
        confidence_path = logs_dir / "confidence_report.json"

        manifest_path.write_text(json.dumps(manifest.model_dump(mode="json"), indent=2), encoding="utf-8")
        scene_graph = build_scene_graph(job_id=job_id, layers=layers)
        scene_graph_path.write_text(json.dumps(scene_graph, indent=2), encoding="utf-8")
        report_path.write_text(
            json.dumps(
                {
                    "job_id": job_id,
                    "status": status,
                    "route": "design_route",
                    "warnings": warnings,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        confidence_path.write_text(
            json.dumps(
                {
                    "job_id": job_id,
                    "global_confidence": global_confidence,
                    "layers": [{"id": layer["id"], "confidence": layer["confidence"]} for layer in layers],
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

        return manifest, manifest_path, archive_path

    @staticmethod
    def _clamp_bbox(bbox: BoundingBox, image_size: tuple[int, int]) -> BoundingBox:
        width, height = image_size
        x = min(max(bbox.x, 0), width - 1)
        y = min(max(bbox.y, 0), height - 1)
        max_width = max(width - x, 1)
        max_height = max(height - y, 1)
        return BoundingBox(
            x=x,
            y=y,
            width=min(bbox.width, max_width),
            height=min(bbox.height, max_height),
        )

    @staticmethod
    def _extract_text_rgba(image: Image.Image, bbox: BoundingBox) -> tuple[Image.Image, Image.Image]:
        crop = image.crop((bbox.x, bbox.y, bbox.x + bbox.width, bbox.y + bbox.height)).convert("RGBA")
        background_color = LocalArtifactStore._estimate_background_color(crop)
        background = Image.new("RGBA", crop.size, color=(*background_color, 255))
        alpha_mask = ImageChops.difference(crop, background).convert("L")
        alpha_mask = alpha_mask.point(lambda value: 255 if value > 20 else 0)
        rgba_crop = crop.copy()
        rgba_crop.putalpha(alpha_mask)
        return rgba_crop, alpha_mask

    @staticmethod
    def _estimate_background_color(crop: Image.Image) -> tuple[int, int, int]:
        rgb_crop = crop.convert("RGB")
        width, height = rgb_crop.size
        pixels: list[tuple[int, int, int]] = []

        for x in range(width):
            pixels.append(rgb_crop.getpixel((x, 0)))
            if height > 1:
                pixels.append(rgb_crop.getpixel((x, height - 1)))
        for y in range(1, height - 1):
            pixels.append(rgb_crop.getpixel((0, y)))
            if width > 1:
                pixels.append(rgb_crop.getpixel((width - 1, y)))

        if not pixels:
            return (255, 255, 255)

        return tuple(int(sum(color[channel] for color in pixels) / len(pixels)) for channel in range(3))

    @staticmethod
    def _estimate_fill_hex(rgba_crop: Image.Image) -> str:
        visible_pixels: list[tuple[int, int, int]] = []
        for red, green, blue, alpha in rgba_crop.getdata():
            if alpha > 0:
                visible_pixels.append((red, green, blue))

        if not visible_pixels:
            return "#000000"

        red = int(sum(pixel[0] for pixel in visible_pixels) / len(visible_pixels))
        green = int(sum(pixel[1] for pixel in visible_pixels) / len(visible_pixels))
        blue = int(sum(pixel[2] for pixel in visible_pixels) / len(visible_pixels))
        return f"#{red:02x}{green:02x}{blue:02x}"

    @staticmethod
    def _build_overlay_debug(image: Image.Image, overlay_path: Path, text_candidates: list[TextCandidate]) -> None:
        from PIL import ImageDraw

        overlay = image.copy()
        draw = ImageDraw.Draw(overlay)
        for candidate in text_candidates:
            bbox = candidate.bbox
            draw.rectangle(
                (bbox.x, bbox.y, bbox.x + bbox.width, bbox.y + bbox.height),
                outline=(255, 0, 0, 255),
                width=1,
            )
        overlay.save(overlay_path)

    @classmethod
    def _compute_global_confidence(cls, layers: list[dict]) -> float:
        non_background_layers = [layer for layer in layers if layer["type"] != "background"]
        if not non_background_layers:
            return 1.0
        return min(float(layer["confidence"]) for layer in non_background_layers)

    @staticmethod
    def _collect_manifest_warnings(layers: list[dict]) -> list[str]:
        warnings: list[str] = []
        for layer in layers:
            for warning in layer.get("warnings", []):
                if warning not in warnings:
                    warnings.append(warning)
        return warnings

    @classmethod
    def _determine_status(cls, global_confidence: float, warnings: list[str]) -> str:
        if global_confidence < cls.LOW_CONFIDENCE_THRESHOLD:
            return "completed_low_confidence"
        if warnings:
            return "completed_with_warnings"
        return "completed_high_confidence"
