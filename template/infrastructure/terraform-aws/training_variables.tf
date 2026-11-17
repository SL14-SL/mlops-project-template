variable "training_task_enabled" {
  description = "Register the Fargate training task definition."
  type        = bool
  default     = false
}

variable "training_image_digest" {
  description = "Digest of the Linux/amd64 training image in the training ECR repository."
  type        = string
  default     = ""

  validation {
    condition = (
      var.training_image_digest == "" ||
      can(regex("^sha256:[a-f0-9]{64}$", var.training_image_digest))
    )
    error_message = "training_image_digest must be empty or a sha256 digest."
  }
}