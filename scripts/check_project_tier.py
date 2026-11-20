"""Verify the scope of an actual Copier-generated project."""

import ast
import sys
import tomllib
from pathlib import Path

root = Path(sys.argv[1])
tier = sys.argv[2]
package = sys.argv[3]
provider = sys.argv[4] if len(sys.argv) > 4 else "gcp"
full = tier == "end_to_end"
aws = provider == "aws"
aws_full = full and aws
cloud = tier != "api"
for relative, expected in {
    "infrastructure": cloud,
    "infrastructure/terraform-aws": cloud and aws,
    "infrastructure/terraform": cloud and not aws,
    "infrastructure/terraform-bootstrap": cloud and not aws,
    "monitoring": cloud,
    ".github/workflows/deploy.yml": cloud and not aws,
    ".github/workflows/deploy-aws.yml": cloud and aws,
    ".github/workflows/lifecycle-aws.yml": aws_full,
    ".github/workflows/verify-mlflow-aws.yml": aws_full,
    ".github/workflows/rollback.yml": cloud and not aws,
    ".github/workflows/rollback-aws.yml": cloud and aws,
    ".github/workflows/terraform.yml": cloud,
    "scripts/export_serving_release_to_cloud.py": cloud,
    "docs/aws-deployment.md": cloud and aws,
    "docs/aws-lifecycle.md": aws_full,
    "docs/aws-mlflow.md": aws_full,
    "infrastructure/terraform-aws/mlflow.tf": aws_full,
    "Dockerfile.mlflow": aws_full,
    "docs/cloud-deployment.md": cloud and not aws,
    "prefect.yaml": full,
    f"src/{package}/pipeline": full,
    f"src/{package}/training": full,
    f"src/{package}/tracking": full,
    f"src/{package}/orchestration": full,
    f"src/{package}/notifications": full,
    f"src/{package}/monitoring/model_observability.py": full,
    "monitoring/grafana/dashboards/model-observability.json": full,
    f"src/{package}/aws": aws_full,
    "tests/unit/aws": aws_full,
    "tests/integration/test_aws_training_job.py": aws_full,
    "Dockerfile.training": aws_full,
    "infrastructure/terraform-aws/training_iam.tf": aws_full,
    "infrastructure/terraform-aws/training_outputs.tf": aws_full,
    "infrastructure/terraform-aws/training_task.tf": aws_full,
    "infrastructure/terraform-aws/training_variables.tf": aws_full,
    "infrastructure/terraform-aws/sagemaker_iam.tf": aws_full,
    "infrastructure/terraform-aws/sagemaker_outputs.tf": aws_full,
    "scripts/training_container_smoke_test.py": aws_full,
    "docs/aws-training.md": aws_full,
}.items():
    assert (root / relative).exists() == expected, relative

dependencies = tomllib.loads((root / "pyproject.toml").read_text())["project"]["dependencies"]
assert any(item.startswith("prefect==") for item in dependencies) == full
assert any(item.startswith("mlflow==") for item in dependencies)
for source in (root / "src").rglob("*.py"):
    ast.parse(source.read_text(), filename=str(source))
assert not list(root.rglob(".terraform"))
print(f"Project scope verified: {tier} / {provider}")
