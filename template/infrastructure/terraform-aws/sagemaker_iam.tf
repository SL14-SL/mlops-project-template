data "aws_iam_policy_document" "sagemaker_trust" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["sagemaker.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [var.aws_account_id]
    }

    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values = [
        "arn:aws:sagemaker:${var.aws_region}:${var.aws_account_id}:*"
      ]
    }
  }
}

resource "aws_iam_role" "sagemaker_training" {
  name               = "${local.name_prefix}-sagemaker-training"
  assume_role_policy = data.aws_iam_policy_document.sagemaker_trust.json
}

data "aws_iam_policy_document" "sagemaker_training" {
  source_policy_documents = [
    data.aws_iam_policy_document.training_task.json
  ]

  statement {
    sid       = "AuthenticateToTrainingEcr"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }

  statement {
    sid = "PullSageMakerTrainingImage"

    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:BatchGetImage",
      "ecr:GetDownloadUrlForLayer"
    ]

    resources = [aws_ecr_repository.training.arn]
  }

  statement {
    sid     = "CreateSageMakerTrainingLogGroup"
    actions = ["logs:CreateLogGroup"]

    resources = [
      "arn:aws:logs:${var.aws_region}:${var.aws_account_id}:log-group:/aws/sagemaker/TrainingJobs",
      "arn:aws:logs:${var.aws_region}:${var.aws_account_id}:log-group:/aws/sagemaker/TrainingJobs:*"
    ]
  }

  statement {
    sid = "WriteSageMakerTrainingLogs"

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
      "logs:DescribeLogStreams"
    ]

    resources = [
      "arn:aws:logs:${var.aws_region}:${var.aws_account_id}:log-group:/aws/sagemaker/TrainingJobs:*"
    ]
  }

  statement {
    sid       = "DescribeTrainingVolumeKey"
    actions   = ["kms:DescribeKey"]
    resources = [aws_kms_key.storage.arn]
  }

  statement {
    sid       = "GrantEncryptedTrainingVolumeAccess"
    actions   = ["kms:CreateGrant"]
    resources = [aws_kms_key.storage.arn]

    condition {
      test     = "Bool"
      variable = "kms:GrantIsForAWSResource"
      values   = ["true"]
    }
  }
}

resource "aws_iam_role_policy" "sagemaker_training" {
  name   = "sagemaker-training-resources"
  role   = aws_iam_role.sagemaker_training.id
  policy = data.aws_iam_policy_document.sagemaker_training.json
}
