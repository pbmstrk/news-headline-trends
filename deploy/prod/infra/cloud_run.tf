data "google_project" "project" {}

resource "google_cloud_run_v2_job" "dataload_job" {
  name                = "monthly-data-load"
  location            = "europe-west1"
  launch_stage        = "GA"
  deletion_protection = false

  template {
    task_count = 1
    template {
      max_retries = 1
      containers {
        image = "europe-west1-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.dataload_repo.name}/data-load:latest"
        resources {
          limits = {
            cpu    = "1"
            memory = "1G"
          }
        }
        dynamic "env" {
          for_each = {
            nyt_api_key       = google_secret_manager_secret.nyt_api_key.secret_id
            jdbc_database_url = google_secret_manager_secret.jdbc_url.secret_id
          }
          content {
            name = env.key
            value_source {
              secret_key_ref {
                secret  = env.value
                version = "latest"
              }
            }
          }
        }
      }
      service_account = google_service_account.cloudrun_job.email
    }
  }
  depends_on = [
    google_project_service.services["run.googleapis.com"]
  ]
}

resource "google_cloud_scheduler_job" "dataload_scheduler" {
  name      = "monthly-data-load"
  region    = "europe-west1"
  schedule  = "0 0 2 * *" # Runs on the 2nd of each month at 00:00 UTC
  time_zone = "UTC"

  http_target {
    http_method = "POST"
    uri         = "https://${google_cloud_run_v2_job.dataload_job.location}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${data.google_project.project.number}/jobs/${google_cloud_run_v2_job.dataload_job.name}:run"
    oauth_token {
      service_account_email = google_service_account.cloudrun_job.email
    }
  }
  depends_on = [google_cloud_run_v2_job.dataload_job]
}