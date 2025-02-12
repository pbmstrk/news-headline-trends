resource "google_service_account" "cloudrun_job" {
  account_id   = "cloudrun-job-sa"
  display_name = "Service Account for Cloud Run Job"
  description  = "Executes the monthly data load job and accesses required secrets"
}

resource "google_service_account" "storage_rw" {
  account_id   = "storage-rw-sa"
  display_name = "Storage Read/Write Service Account"
  description  = "Handles read/write operations for data backup storage bucket"
}

resource "google_service_account_key" "key" {
  service_account_id = google_service_account.storage_rw.name
}

resource "google_secret_manager_secret_iam_member" "cloudrun_secret_access" {
  for_each = {
    jdbc_url    = google_secret_manager_secret.jdbc_url.id
    nyt_api_key = google_secret_manager_secret.nyt_api_key.id
  }

  secret_id = each.value
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloudrun_job.email}"
}

resource "google_project_iam_member" "cloudrun_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.cloudrun_job.email}"
}

resource "google_artifact_registry_repository_iam_member" "cloudrun_registry_access" {
  repository = google_artifact_registry_repository.dataload_repo.name
  location   = google_artifact_registry_repository.dataload_repo.location
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.cloudrun_job.email}"
  depends_on = [
    google_project_service.services["artifactregistry.googleapis.com"]
  ]
}

resource "google_storage_bucket_iam_member" "storage_access" {
  bucket = google_storage_bucket.data_backup.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.storage_rw.email}"
}