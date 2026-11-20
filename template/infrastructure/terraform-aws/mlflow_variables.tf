variable "mlflow_tracking_uri" {
  description = "Reachable shared MLflow tracking/registry HTTPS endpoint with a durable DB backend."
  type        = string
  default     = ""
  validation {
    condition     = !var.training_task_enabled || var.mlflow_managed_enabled || can(regex("^https://[^/]+", var.mlflow_tracking_uri))
    error_message = "Set the shared HTTPS MLflow endpoint; job-local SQLite is not a registry."
  }
}

variable "prefect_api_url" {
  description = "Optional reachable Prefect API. Empty uses an ephemeral local Prefect server."
  type        = string
  default     = ""
}

variable "mlflow_token_secret_arn" {
  description = "Optional Secrets Manager ARN containing MLFLOW_TRACKING_TOKEN."
  type        = string
  default     = ""
}

variable "prefect_key_secret_arn" {
  description = "Optional Secrets Manager ARN containing PREFECT_API_KEY."
  type        = string
  default     = ""
}


variable "mlflow_managed_enabled" {
  description = "Provision MLflow, RDS PostgreSQL and an authenticated HTTPS gateway."
  type        = bool
  default     = false
}

variable "mlflow_image_digest" {
  description = "Digest of Dockerfile.mlflow image; required for managed MLflow."
  type        = string
  default     = ""
}

variable "mlflow_desired_count" {
  type    = number
  default = 1
  validation {
    condition     = contains([0, 1], var.mlflow_desired_count)
    error_message = "Use zero or one MLflow task; this deployment is single-instance."
  }
}

variable "mlflow_database_deletion_protection" {
  type    = bool
  default = true
}

variable "mlflow_final_snapshot_identifier" {
  description = "Unique final snapshot name when deleting the database."
  type        = string
  default     = ""
}
