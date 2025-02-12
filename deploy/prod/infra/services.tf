resource "google_project_service" "services" {
  for_each = toset([
    "run.googleapis.com",
    "cloudscheduler.googleapis.com",
    "iam.googleapis.com",
    "artifactregistry.googleapis.com",
    "secretmanager.googleapis.com"
  ])
  service = each.key
}

# Artifact Registry
resource "google_artifact_registry_repository" "dataload_repo" {
  location      = "europe-west1"
  repository_id = "data-load"
  format        = "DOCKER"
  depends_on    = [google_project_service.services["artifactregistry.googleapis.com"]]
}
