variable "mlflow_managed_enabled" {
  type    = bool
  default = false
  validation {
    condition     = !var.mlflow_managed_enabled
    error_message = "Managed MLflow requires the end_to_end tier."
  }
}
variable "mlflow_image_digest" {
  type    = string
  default = ""
}
output "mlflow_managed_enabled" { value = false }
