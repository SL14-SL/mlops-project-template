output "aws_region" {
  value = var.aws_region
}

output "artifact_bucket_name" {
  value = aws_s3_bucket.artifacts.id
}

output "data_root_uri" {
  value = "s3://${aws_s3_bucket.artifacts.id}/data"
}

output "models_uri" {
  value = "s3://${aws_s3_bucket.artifacts.id}/models"
}

output "api_repository_url" {
  value = aws_ecr_repository.api.repository_url
}

output "storage_kms_key_arn" {
  value = aws_kms_key.storage.arn
}