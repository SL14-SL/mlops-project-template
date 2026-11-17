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