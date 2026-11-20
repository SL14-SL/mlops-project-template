resource "aws_ecr_repository" "training" {
  name                 = "${local.name_prefix}-training"
  image_tag_mutability = "IMMUTABLE"
  force_delete         = false

  encryption_configuration {
    encryption_type = "KMS"
    kms_key         = aws_kms_key.storage.arn
  }

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_cloudwatch_log_group" "training" {
  name              = "/ecs/${local.name_prefix}-training"
  retention_in_days = 14
}

resource "aws_iam_role" "training_execution" {
  name               = "${local.name_prefix}-training-execution"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_trust.json
}

data "aws_iam_policy_document" "training_execution" {
  dynamic "statement" {
    for_each = length(compact([local.mlflow_token_secret_arn, var.prefect_key_secret_arn])) > 0 ? [1] : []
    content {
      actions   = ["secretsmanager:GetSecretValue"]
      resources = compact([local.mlflow_token_secret_arn, var.prefect_key_secret_arn])
    }
  }
  statement {
    sid       = "AuthenticateToEcr"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }

  statement {
    sid = "PullTrainingImage"

    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:BatchGetImage",
      "ecr:GetDownloadUrlForLayer"
    ]

    resources = [aws_ecr_repository.training.arn]
  }

  statement {
    sid = "WriteTrainingLogs"

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = ["${aws_cloudwatch_log_group.training.arn}:*"]
  }
}

resource "aws_iam_role_policy" "training_execution" {
  name   = "training-image-and-logs"
  role   = aws_iam_role.training_execution.id
  policy = data.aws_iam_policy_document.training_execution.json
}

resource "aws_iam_role" "training_task" {
  name               = "${local.name_prefix}-training-task"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_trust.json
}

data "aws_iam_policy_document" "training_task" {
  statement {
    sid       = "LifecycleObjects"
    actions   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:AbortMultipartUpload"]
    resources = [for prefix in ["data", "models", "artifacts", "mlflow"] : "${aws_s3_bucket.artifacts.arn}/${prefix}/*"]
  }
  statement {
    sid       = "RefreshApi"
    actions   = ["ecs:DescribeServices", "ecs:UpdateService"]
    resources = ["arn:aws:ecs:${var.aws_region}:${var.aws_account_id}:service/${aws_ecs_cluster.main.name}/${local.name_prefix}-api"]
  }

  statement {
    sid       = "ReadBucketLocation"
    actions   = ["s3:GetBucketLocation"]
    resources = [aws_s3_bucket.artifacts.arn]
  }

  statement {
    sid       = "ListTrainingInputs"
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.artifacts.arn]

    condition {
      test     = "StringLike"
      variable = "s3:prefix"

      values = [
        "training/input",
        "training/input/*", "data", "data/*", "models", "models/*", "artifacts", "artifacts/*", "mlflow", "mlflow/*"
      ]
    }
  }

  statement {
    sid       = "ReadTrainingInputs"
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.artifacts.arn}/training/input/*"]
  }

  statement {
    sid = "WriteTrainingResults"

    actions = [
      "s3:PutObject",
      "s3:AbortMultipartUpload"
    ]

    resources = ["${aws_s3_bucket.artifacts.arn}/training/output/*"]
  }

  statement {
    sid = "UseTrainingEncryption"

    actions = [
      "kms:Decrypt",
      "kms:GenerateDataKey"
    ]

    resources = [aws_kms_key.storage.arn]

    condition {
      test     = "StringEquals"
      variable = "kms:ViaService"
      values   = ["s3.${var.aws_region}.amazonaws.com"]
    }

    condition {
      test     = "StringLike"
      variable = "kms:EncryptionContext:aws:s3:arn"

      values = [
        aws_s3_bucket.artifacts.arn,
        "${aws_s3_bucket.artifacts.arn}/*",
        "${aws_s3_bucket.artifacts.arn}/training/input/*",
        "${aws_s3_bucket.artifacts.arn}/training/output/*"
      ]
    }
  }
}

resource "aws_iam_role_policy" "training_task" {
  name   = "training-inputs-and-results"
  role   = aws_iam_role.training_task.id
  policy = data.aws_iam_policy_document.training_task.json
}
