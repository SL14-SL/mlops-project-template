"""Verify the scope of an actual Copier-generated project."""
import ast
import sys
import tomllib
from pathlib import Path

root = Path(sys.argv[1])
tier = sys.argv[2]
package = sys.argv[3]
full = tier == "end_to_end"
cloud = tier != "api"
for relative, expected in {
    "infrastructure": cloud,
    "monitoring": cloud,
    ".github/workflows/deploy.yml": cloud,
    ".github/workflows/rollback.yml": cloud,
    ".github/workflows/terraform.yml": cloud,
    "scripts/export_serving_release_to_cloud.py": cloud,
    "prefect.yaml": full,
    f"src/{package}/pipeline": full,
    f"src/{package}/training": full,
    f"src/{package}/tracking": full,
    f"src/{package}/orchestration": full,
    f"src/{package}/notifications": full,
    f"src/{package}/monitoring/model_observability.py": full,
    "monitoring/grafana/dashboards/model-observability.json": full,
}.items():
    assert (root / relative).exists() == expected, relative

dependencies = tomllib.loads((root / "pyproject.toml").read_text())["project"]["dependencies"]
assert any(item.startswith("prefect==") for item in dependencies) == full
assert any(item.startswith("mlflow==") for item in dependencies)
for source in (root / "src").rglob("*.py"):
    ast.parse(source.read_text(), filename=str(source))
assert not list(root.rglob(".terraform"))
print(f"Project tier scope verified: {tier}")
