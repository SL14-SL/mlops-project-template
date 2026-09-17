variable "gcp_project_id" {
  description = "Google Cloud project used for the deployment."
  type        = string

  validation {
    condition     = length(trimspace(var.gcp_project_id)) > 0
    error_message = "gcp_project_id must not be empty."
  }
}

variable "region" {
  description = "Google Cloud region for regional resources."
  type        = string
  default     = "europe-west1"
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "dev"

  validation {
    condition = contains(
      [
        "dev",
        "staging",
        "prod",
      ],
      var.environment,
    )

    error_message = "environment must be dev, staging or prod."
  }
}

variable "artifact_registry_repository" {
  description = "Artifact Registry repository name."
  type        = string
  default     = "mlops-images"
}

variable "storage_location" {
  description = "Location used for the MLOps artifact bucket."
  type        = string
  default     = "EU"
}

variable "force_destroy_artifact_bucket" {
  description = "Allow Terraform to remove a non-empty artifact bucket."
  type        = bool
  default     = false
}