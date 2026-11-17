"""Download S3 inputs, run isolated training, and upload candidate artifacts."""

import argparse
import json
import subprocess
import sys
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from typing import Any
from urllib.parse import urlsplit
from uuid import uuid4

from ..inference.releases.storage import sha256_uri


def parse_s3_prefix(uri: str) -> tuple[str, str]:
    """Parse an S3 bucket and non-empty object prefix."""
    parsed = urlsplit(uri)

    if (
        parsed.scheme != "s3"
        or not parsed.netloc
        or parsed.query
        or parsed.fragment
        or ":" in parsed.netloc
        or "@" in parsed.netloc
    ):
        raise ValueError("Expected an S3 URI containing a bucket and prefix.")

    prefix = parsed.path.strip("/")

    if not prefix:
        raise ValueError("An S3 object prefix is required.")

    return parsed.netloc, prefix


def _safe_relative_path(value: str) -> str:
    """Reject object names that could escape a local directory."""
    path = PurePosixPath(value)

    if (
        not value
        or path.is_absolute()
        or "\\" in value
        or ":" in value
        or ".." in path.parts
        or value == "."
        or value != path.as_posix()
    ):
        raise ValueError(f"Unsafe relative object path: {value!r}")

    return value


def run_fargate_training(
    *,
    input_uri: str,
    output_uri: str,
    config_path: Path,
    timeout_seconds: int = 900,
    s3_client: Any = None,
) -> dict[str, Any]:
    """Run one training job and publish its completion marker last."""
    input_bucket, input_prefix = parse_s3_prefix(input_uri)
    output_bucket, output_prefix = parse_s3_prefix(output_uri)

    if input_bucket == output_bucket:
        if (
            input_prefix == output_prefix
            or input_prefix.startswith(f"{output_prefix}/")
            or output_prefix.startswith(f"{input_prefix}/")
        ):
            raise ValueError("Training input and output prefixes must not overlap.")

    config_path = config_path.resolve()

    if not config_path.is_file():
        raise FileNotFoundError(config_path)

    if timeout_seconds <= 0:
        raise ValueError("Training timeout must be positive.")

    if s3_client is None:
        import boto3

        s3_client = boto3.client("s3")

    job_id = f"fargate-{uuid4().hex}"
    result_prefix = f"{output_prefix}/{job_id}"

    with TemporaryDirectory(prefix="mlops-training-") as temporary:
        root = Path(temporary)
        input_directory = root / "input"
        input_directory.mkdir()
        prefix = f"{input_prefix}/"
        downloaded_files = 0

        paginator = s3_client.get_paginator("list_objects_v2")

        for page in paginator.paginate(
            Bucket=input_bucket,
            Prefix=prefix,
        ):
            for item in page.get("Contents", []):
                key = item["Key"]

                if key.endswith("/"):
                    continue

                if not key.startswith(prefix):
                    raise ValueError("S3 returned an object outside the input prefix.")

                relative_path = _safe_relative_path(key[len(prefix) :])
                destination = input_directory / relative_path
                destination.parent.mkdir(parents=True, exist_ok=True)

                s3_client.download_file(
                    input_bucket,
                    key,
                    str(destination),
                )
                downloaded_files += 1

        if downloaded_files == 0:
            raise FileNotFoundError(f"No training input files found at {input_uri}")

        subprocess.run(
            [
                sys.executable,
                "-m",
                f"{__package__}.train",
                "--config",
                str(config_path),
                "--input-dir",
                str(input_directory),
                "--work-dir",
                str(root / "work"),
                "--model-dir",
                str(root / "model"),
                "--output-dir",
                str(root / "output"),
            ],
            check=True,
            timeout=timeout_seconds,
        )

        required_files = (
            root / "model/model/MLmodel",
            root / "model/candidate.json",
            root / "output/evaluation.json",
        )

        for required in required_files:
            if not required.is_file():
                raise FileNotFoundError(f"Training did not export required file: {required}")

        candidate = json.loads((root / "model/candidate.json").read_text(encoding="utf-8"))
        evaluation = json.loads((root / "output/evaluation.json").read_text(encoding="utf-8"))

        if (
            candidate.get("schema_version") != 1
            or evaluation.get("schema_version") != 1
            or not evaluation.get("run_id")
            or candidate.get("run_id") != evaluation["run_id"]
            or candidate.get("promoted") is not False
            or evaluation.get("promoted") is not False
            or type(evaluation.get("evaluation_approved")) is not bool
        ):
            raise ValueError("Training exported inconsistent candidate metadata.")

        inventory = []

        for directory_name in ("model", "output"):
            directory = root / directory_name

            for file in sorted(directory.rglob("*")):
                if file.is_symlink():
                    raise ValueError("Training exports must not contain symlinks.")

                if not file.is_file():
                    continue

                relative_path = file.relative_to(root).as_posix()
                checksum = sha256_uri(str(file))

                s3_client.upload_file(
                    str(file),
                    output_bucket,
                    f"{result_prefix}/{relative_path}",
                )
                inventory.append(
                    {
                        "path": relative_path,
                        "sha256": checksum,
                    }
                )

        completion = {
            "schema_version": 1,
            "status": "completed",
            "job_id": job_id,
            "run_id": evaluation["run_id"],
            "evaluation_approved": evaluation["evaluation_approved"],
            "promoted": False,
            "result_uri": f"s3://{output_bucket}/{result_prefix}",
            "files": inventory,
        }

        s3_client.put_object(
            Bucket=output_bucket,
            Key=f"{result_prefix}/completion.json",
            Body=json.dumps(
                completion,
                indent=2,
                sort_keys=True,
                allow_nan=False,
            ).encode("utf-8"),
            ContentType="application/json",
            IfNoneMatch="*",
        )

    return completion


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-uri", required=True)
    parser.add_argument("--output-uri", required=True)
    parser.add_argument("--config", type=Path, default=Path("configs/dev.yaml"))
    parser.add_argument("--timeout-seconds", type=int, default=900)
    args = parser.parse_args()

    completion = run_fargate_training(
        input_uri=args.input_uri,
        output_uri=args.output_uri,
        config_path=args.config,
        timeout_seconds=args.timeout_seconds,
    )
    print(json.dumps(completion, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
