output "sagemaker_training_role_arn" {
  value = aws_iam_role.sagemaker_training.arn
}

output "sagemaker_training_log_group_name" {
  value = "/aws/sagemaker/TrainingJobs"
}