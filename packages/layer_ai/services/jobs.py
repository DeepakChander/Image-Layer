from datetime import UTC, datetime

from layer_ai.config import Settings
from layer_ai.contracts.models import JobRecord, JobStatus
from layer_ai.errors import InvalidImageError
from layer_ai.storage.local import LocalArtifactStore
from layer_ai.text.base import TextExtractor
from layer_ai.visual.base import VisualExtractor


class JobService:
    def __init__(
        self,
        settings: Settings,
        text_extractor: TextExtractor,
        visual_extractor: VisualExtractor,
    ) -> None:
        self.settings = settings
        self.store = LocalArtifactStore(settings.storage_root)
        self.text_extractor = text_extractor
        self.visual_extractor = visual_extractor

    async def create_job(self, image_bytes: bytes, filename: str, instruction: str) -> JobRecord:
        if not image_bytes:
            raise InvalidImageError("Image file is empty")

        job_id = self.store.next_job_id()
        record = JobRecord(
            job_id=job_id,
            status=JobStatus.QUEUED,
            route="design_route",
            global_confidence=None,
            instruction=instruction,
            created_at=datetime.now(UTC).isoformat(),
            artifact_zip_path=None,
        )
        self.store.write_job_record(record)

        record = record.model_copy(update={"status": JobStatus.PREPROCESSING})
        self.store.write_job_record(record)

        try:
            manifest, manifest_path, asset_zip_path = self.store.build_package(
                job_id=job_id,
                image_bytes=image_bytes,
                filename=filename,
                text_extractor=self.text_extractor,
                visual_extractor=self.visual_extractor,
                editable_text_confidence_threshold=self.settings.editable_text_confidence_threshold,
            )

            record = record.model_copy(
                update={
                    "status": JobStatus(manifest.status),
                    "global_confidence": manifest.global_confidence,
                    "artifact_zip_path": str(asset_zip_path),
                }
            )
            self.store.write_job_record(record)
            self.store.write_manifest_pointer(job_id, manifest_path)
            return record
        except Exception:
            failed_record = record.model_copy(update={"status": JobStatus.FAILED_PROCESSING_ERROR})
            self.store.write_job_record(failed_record)
            raise

    def get_job(self, job_id: str) -> JobRecord | None:
        return self.store.read_job_record(job_id)

    def get_manifest(self, job_id: str) -> dict | None:
        return self.store.read_manifest(job_id)

    def get_assets_archive(self, job_id: str) -> str | None:
        record = self.get_job(job_id)
        if record is None:
            return None
        return record.artifact_zip_path
