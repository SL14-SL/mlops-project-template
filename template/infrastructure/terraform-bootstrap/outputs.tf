output "terraform_state_bucket" {
  description = "GCS bucket used for the primary Terraform state."
  value       = google_storage_bucket.terraform_state.name
}