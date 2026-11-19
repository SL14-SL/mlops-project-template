"""Render all task/tier/provider combinations and optionally test each project."""

import argparse
import subprocess
import sys
from itertools import product
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tests", action="store_true", help="Sync and run generated Ruff/pytest checks"
    )
    parser.add_argument("--output", type=Path, default=Path("generated/cloud-matrix"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    for task, tier, provider in product(
        ("classification", "forecasting"), ("api", "deployment", "end_to_end"), ("gcp", "aws")
    ):
        target = args.output.resolve() / f"{task}-{tier}-{provider}"
        subprocess.run(
            [
                sys.executable,
                "-m",
                "copier",
                "copy",
                "--defaults",
                "--overwrite",
                "--vcs-ref=HEAD",
                "--data",
                "project_slug=matrix-check",
                "--data",
                f"task_type={task}",
                "--data",
                f"project_tier={tier}",
                "--data",
                f"cloud_provider={provider}",
                str(root),
                str(target),
            ],
            check=True,
        )
        subprocess.run(
            [
                sys.executable,
                str(root / "scripts/check_project_tier.py"),
                str(target),
                tier,
                "matrix_check",
                provider,
            ],
            check=True,
        )
        if args.tests:
            for command in (
                ["uv", "sync", "--extra", "aws"],
                ["uv", "run", "--locked", "--extra", "aws", "ruff", "check", "."],
                ["uv", "run", "--locked", "--extra", "aws", "pytest", "-q"],
            ):
                subprocess.run(command, cwd=target, check=True)
        print(f"Verified {task} / {tier} / {provider}", flush=True)


if __name__ == "__main__":
    main()
