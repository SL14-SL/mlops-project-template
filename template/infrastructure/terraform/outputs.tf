output "artifact_registry_repository" {
  description = "Artifact Registry repository resource name."
  value       = google_artifact_registry_repository.containers.name
}

output "artifact_registry_image_prefix" {
  description = "Prefix used when publishing container images."
  value = join(
    "/",
    [
      "${var.region}-docker.pkg.dev",
      var.gcp_project_id,
      google_artifact_registry_repository.containers.repository_id,
    ],
  )
}

output "artifact_bucket_name" {
  description = "GCS bucket used for MLOps artifacts."
  value       = google_storage_bucket.artifacts.name
}

output "api_service_account_email" {
  description = "Service account used by the serving API."
  value       = google_service_account.api.email
}

output "cloud_run_service_name" {
  description = "Name of the deployed Cloud Run service."
  value       = google_cloud_run_v2_service.api.name
}

output "cloud_run_service_uri" {
  description = "URI assigned to the Cloud Run service."
  value       = google_cloud_run_v2_service.api.uri
}

output "api_key_secret_name" {
  description = "Secret Manager secret containing the API key."
  value       = google_secret_manager_secret.api_key.secret_id
}