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

output "vpc_id" {
  value = aws_vpc.main.id
}

output "api_subnet_ids" {
  value = aws_subnet.public[*].id
}

output "api_execution_role_arn" {
  value = aws_iam_role.api_execution.arn
}

output "api_task_role_arn" {
  value = aws_iam_role.api_task.arn
}

output "api_key_secret_arn" {
  value = aws_secretsmanager_secret.api_key.arn
}

output "api_log_group" {
  value = aws_cloudwatch_log_group.api.name
}

output "api_cluster_arn" {
  value = aws_ecs_cluster.main.arn
}

output "api_task_definition_arn" {
  value = var.api_serving_enabled ? aws_ecs_task_definition.api[0].arn : null
}

output "api_service_name" {
  value = var.api_serving_enabled ? aws_ecs_service.api[0].name : null
}

output "api_endpoint" {
  value = var.api_serving_enabled ? aws_apigatewayv2_api.api[0].api_endpoint : null
}

output "api_gateway_log_group" {
  value = aws_cloudwatch_log_group.api_gateway.name
}
output "api_image_uri" {
  value = "${aws_ecr_repository.api.repository_url}@${var.api_image_digest}"
}
output "serving_models_uri" {
  value = "s3://${aws_s3_bucket.artifacts.id}/models"
}
