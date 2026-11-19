"""Initialize the API secret outside Terraform without replacing an existing key."""

import json
import secrets
import subprocess


def main():
    raw = subprocess.check_output(
        ["terraform", "-chdir=infrastructure/terraform-aws", "output", "-json"]
    )
    arn = json.loads(raw)["api_key_secret_arn"]["value"]
    metadata = json.loads(
        subprocess.check_output(
            ["aws", "secretsmanager", "describe-secret", "--secret-id", arn, "--output", "json"]
        )
    )
    if any("AWSCURRENT" in stages for stages in metadata.get("VersionIdsToStages", {}).values()):
        print("Existing API key retained.")
        return
    subprocess.run(
        ["aws", "secretsmanager", "put-secret-value", "--cli-input-json", "file:///dev/stdin"],
        input=json.dumps({"SecretId": arn, "SecretString": secrets.token_urlsafe(48)}),
        text=True,
        capture_output=True,
        check=True,
    )
    print("API key initialized.")


if __name__ == "__main__":
    main()
