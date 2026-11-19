"""Preserve deployed variables while replacing only the API image digest."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path


def validate_plan(plan):
    allowed = {"aws_ecs_task_definition.api[0]", "aws_ecs_service.api[0]"}
    unexpected = [
        item["address"]
        for item in plan.get("resource_changes", [])
        if item["change"]["actions"] not in (["no-op"], ["read"]) and item["address"] not in allowed
    ]
    if unexpected:
        raise ValueError("Rollback would change unrelated resources: " + ", ".join(unexpected))


def main():
    if sys.argv[1:] == ["--check-plan"]:
        validate_plan(
            json.loads(
                subprocess.check_output(
                    [
                        "terraform",
                        "-chdir=infrastructure/terraform-aws",
                        "show",
                        "-json",
                        "rollback.tfplan",
                    ]
                )
            )
        )
        return
    digest = os.environ["API_DIGEST"]
    if not re.fullmatch(r"sha256:[a-f0-9]{64}", digest):
        raise ValueError("Expected an immutable API sha256 digest.")
    state = json.loads(
        subprocess.check_output(
            ["terraform", "-chdir=infrastructure/terraform-aws", "state", "pull"]
        )
    )
    resources = state.get("resources", [])
    values = {}
    for resource in resources:
        if resource["type"] == "aws_ecs_task_definition" and resource["name"] in {
            "api",
            "training",
            "mlflow",
        }:
            for instance in resource["instances"]:
                containers = json.loads(instance["attributes"]["container_definitions"])
                for item in containers:
                    for env in item.get("environment", []):
                        if env["name"] in {
                            "APP_ENV",
                            "AWS_REGION",
                            "PREFECT_API_URL",
                            "MLFLOW_TRACKING_URI",
                        }:
                            values[env["name"]] = env["value"]
    outputs = {key: item["value"] for key, item in state["outputs"].items()}
    managed = outputs.get("mlflow_managed_enabled", False)
    account = json.loads(
        subprocess.check_output(["aws", "sts", "get-caller-identity", "--output", "json"])
    )["Account"]
    variables = {
        "aws_account_id": account,
        "aws_region": outputs["aws_region"],
        "environment": values.get("APP_ENV", "dev"),
        "api_serving_enabled": True,
        "api_image_digest": digest,
    }
    if "training_image_uri" in outputs:
        variables.update(
            training_task_enabled=bool(outputs.get("training_task_definition_arn")),
            training_image_digest=outputs["training_image_uri"].split("@")[-1],
            mlflow_managed_enabled=managed,
            mlflow_image_digest=(outputs.get("mlflow_image_uri") or "@").split("@")[-1],
            mlflow_tracking_uri=outputs.get("mlflow_tracking_uri", ""),
            prefect_api_url=values.get("PREFECT_API_URL", ""),
        )
        # Retain externally configured secret references from the existing task definition.
        for resource in resources:
            if resource["type"] == "aws_ecs_task_definition" and resource["name"] == "training":
                for instance in resource["instances"]:
                    for container in json.loads(instance["attributes"]["container_definitions"]):
                        for secret in container.get("secrets", []):
                            name = {
                                "MLFLOW_TRACKING_TOKEN": "mlflow_token_secret_arn",
                                "PREFECT_API_KEY": "prefect_key_secret_arn",
                            }.get(secret["name"])
                            if name and (not managed or name == "prefect_key_secret_arn"):
                                variables[name] = secret["valueFrom"]
    Path("infrastructure/terraform-aws/rollback.auto.tfvars.json").write_text(
        json.dumps(variables, indent=2)
    )


if __name__ == "__main__":
    main()
