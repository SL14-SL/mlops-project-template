output "mlflow_managed_enabled" {
  value = var.mlflow_managed_enabled
}
output "mlflow_tracking_uri" {
  value = local.mlflow_tracking_uri
}
output "mlflow_token_secret_arn" {
  value = local.mlflow_token_secret_arn
}
output "mlflow_repository_url" {
  value = var.mlflow_managed_enabled ? aws_ecr_repository.mlflow[0].repository_url : null
}
output "mlflow_image_uri" {
  value = var.mlflow_managed_enabled ? "${aws_ecr_repository.mlflow[0].repository_url}@${var.mlflow_image_digest}" : null
}
output "mlflow_service_name" {
  value = var.mlflow_managed_enabled ? aws_ecs_service.mlflow[0].name : null
}
output "mlflow_database_identifier" {
  value = var.mlflow_managed_enabled ? aws_db_instance.mlflow[0].identifier : null
}

output "training_bucket_name" {
  value = aws_s3_bucket.artifacts.id
}
