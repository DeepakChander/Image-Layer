import argparse
import json
import sys
from pathlib import Path

from layer_ai.config import Settings
from layer_ai.errors import RendererJobNotReadyError
from layer_ai.renderers.base import UnsupportedRendererError
from layer_ai.services.jobs import JobService
from layer_ai.text.noop import NoopTextExtractor
from layer_ai.visual.noop import NoopVisualExtractor


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a local renderer handoff payload for an existing job.")
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--renderer", required=True)
    parser.add_argument("--storage-root", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    settings = Settings(storage_root=Path(args.storage_root)) if args.storage_root else Settings()
    job_service = JobService(
        settings,
        text_extractor=NoopTextExtractor(),
        visual_extractor=NoopVisualExtractor(),
    )

    try:
        result = job_service.create_renderer_handoff(args.job_id, args.renderer)
    except (FileNotFoundError, RendererJobNotReadyError, UnsupportedRendererError) as error:
        print(str(error), file=sys.stderr)
        return 1

    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
