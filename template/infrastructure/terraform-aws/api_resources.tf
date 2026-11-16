resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/${local.name_prefix}-api"
  retention_in_days = 14
}

resource "aws_secretsmanager_secret" "api_key" {
  name                    = "${local.name_prefix}/api-key"
  description             = "Application API key for the forecasting or classification API"
  kms_key_id              = aws_kms_key.storage.arn
  recovery_window_in_days = 7
}