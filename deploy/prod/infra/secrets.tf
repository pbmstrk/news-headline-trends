resource "google_secret_manager_secret" "jdbc_url" {
  secret_id = "JDBC_DATABASE_URL"
  replication {
    auto {}
  }
  depends_on = [google_project_service.services["secretmanager.googleapis.com"]]
}

resource "google_secret_manager_secret" "nyt_api_key" {
  secret_id = "NYT_API_KEY"
  replication {
    auto {}
  }
  depends_on = [google_project_service.services["secretmanager.googleapis.com"]]
}

resource "google_secret_manager_secret_version" "jdbc_url_value" {
  secret = google_secret_manager_secret.jdbc_url.id
  secret_data = format("jdbc:postgresql://%s:%s/%s?sslmode=verify-full&password=%s&user=%s",
    data.cockroach_connection_string.db_conn_string.connection_params.host,
    data.cockroach_connection_string.db_conn_string.connection_params.port,
    data.cockroach_connection_string.db_conn_string.connection_params.database,
    data.cockroach_connection_string.db_conn_string.connection_params.password,
    data.cockroach_connection_string.db_conn_string.connection_params.username
  )
}

resource "google_secret_manager_secret_version" "nyt_api_key_value" {
  secret      = google_secret_manager_secret.nyt_api_key.id
  secret_data = var.nyt_api_key
}