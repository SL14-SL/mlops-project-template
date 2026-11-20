"""Build a SageMaker training request without submitting it."""

import argparse
import json
import re
from typing import Any

from .fargate_train import parse_s3_prefix


def build_sagemaker_training_job(
    *,
    job_name: str,
    role_arn: str,
    image_uri: str,
    input_uri: str,
    output_uri: str,
    kms_key_arn: str,
) -> dict[str, Any]:
    """Configure a single-instance, network-isolated training job."""
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", job_name):
        raise ValueError("SageMaker job name must contain 1–63 letters, digits or hyphens.")

    if not re.fullmatch(r"arn:aws:iam::[0-9]{12}:role/[A-Za-z0-9+=,.@_/-]+", role_arn):
        raise ValueError("Expected an AWS IAM role ARN.")

    image_match = re.fullmatch(
        r"([0-9]{12})\.dkr\.ecr\.([a-z0-9-]+)\.amazonaws\.com/"
        r"[a-z0-9/_-]+@sha256:[a-f0-9]{64}",
        image_uri,
    )

    if image_match is None:
        raise ValueError("Expected a private ECR image URI pinned by sha256 digest.")

    kms_match = re.fullmatch(
        r"arn:aws:kms:([a-z0-9-]+):([0-9]{12}):key/[A-Za-z0-9-]+",
        kms_key_arn,
    )

    if kms_match is None:
        raise ValueError("Expected an AWS KMS key ARN.")

    account_id, region = image_match.groups()

    if (
        kms_match.group(1) != region
        or kms_match.group(2) != account_id
        or role_arn.split(":")[4] != account_id
    ):
        raise ValueError("Image, role and KMS key must use the same account and region.")

    input_bucket, input_prefix = parse_s3_prefix(input_uri)
    output_bucket, output_prefix = parse_s3_prefix(output_uri)

    if input_bucket == output_bucket and (
        input_prefix == output_prefix
        or input_prefix.startswith(f"{output_prefix}/")
        or output_prefix.startswith(f"{input_prefix}/")
    ):
        raise ValueError("Training input and output prefixes must not overlap.")

    return {
        "TrainingJobName": job_name,
        "RoleArn": role_arn,
        "AlgorithmSpecification": {
            "TrainingImage": image_uri,
            "TrainingInputMode": "File",
            "ContainerEntrypoint": [
                "python",
                "-m",
                f"{__package__}.train",
            ],
            "ContainerArguments": [
                "train",
                "--config",
                "/app/configs/dev.yaml",
                "--input-dir",
                "/opt/ml/input/data/training",
                "--work-dir",
                "/tmp/mlops-training-work",
                "--model-dir",
                "/opt/ml/model",
                "--output-dir",
                "/opt/ml/output/data",
            ],
        },
        "InputDataConfig": [
            {
                "ChannelName": "training",
                "DataSource": {
                    "S3DataSource": {
                        "S3DataType": "S3Prefix",
                        "S3Uri": f"s3://{input_bucket}/{input_prefix}/",
                        "S3DataDistributionType": "FullyReplicated",
                    },
                },
            },
        ],
        "OutputDataConfig": {
            "S3OutputPath": f"s3://{output_bucket}/{output_prefix}",
            "KmsKeyId": kms_key_arn,
        },
        "ResourceConfig": {
            "InstanceType": "ml.m5.xlarge",
            "InstanceCount": 1,
            "VolumeSizeInGB": 20,
            "VolumeKmsKeyId": kms_key_arn,
        },
        "StoppingCondition": {
            "MaxRuntimeInSeconds": 900,
        },
        "EnableNetworkIsolation": True,
        "EnableInterContainerTrafficEncryption": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job-name", required=True)
    parser.add_argument("--role-arn", required=True)
    parser.add_argument("--image-uri", required=True)
    parser.add_argument("--input-uri", required=True)
    parser.add_argument("--output-uri", required=True)
    parser.add_argument("--kms-key-arn", required=True)
    args = parser.parse_args()

    request = build_sagemaker_training_job(
        job_name=args.job_name,
        role_arn=args.role_arn,
        image_uri=args.image_uri,
        input_uri=args.input_uri,
        output_uri=args.output_uri,
        kms_key_arn=args.kms_key_arn,
    )
    print(json.dumps(request, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
