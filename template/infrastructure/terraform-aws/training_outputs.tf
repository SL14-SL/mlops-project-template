output "training_repository_url" {
  value = aws_ecr_repository.training.repository_url
}

output "training_input_uri" {
  value = "s3://${aws_s3_bucket.artifacts.id}/training/input"
}

output "training_output_uri" {
  value = "s3://${aws_s3_bucket.artifacts.id}/training/output"
}

output "training_execution_role_arn" {
  value = aws_iam_role.training_execution.arn
}

output "training_task_role_arn" {
  value = aws_iam_role.training_task.arn
}

output "training_log_group" {
  value = aws_cloudwatch_log_group.training.name
}

output "training_cluster_arn" {
  value = aws_ecs_cluster.main.arn
}

output "training_task_definition_arn" {
  value = var.training_task_enabled ? aws_ecs_task_definition.training[0].arn : null
}

output "training_security_group_id" {
  value = aws_security_group.training_task.id
}

output "training_subnet_ids" {
  value = aws_subnet.public[*].id
}
output "training_image_uri" {
  value = "${aws_ecr_repository.training.repository_url}@${var.training_image_digest}"
}
