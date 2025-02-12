output "redis_url" {
  description = "The Redis connection URL"
  value = format("redis://default:%s@%s:%s",
    upstash_redis_database.cache_db.password,
    upstash_redis_database.cache_db.endpoint,
  upstash_redis_database.cache_db.port)
  sensitive = true
}

output "cockroach_connection_string" {
  description = "The CockroachDB connection string"
  value       = data.cockroach_connection_string.db_conn_string.connection_string
  sensitive   = true
}

output "service_account_key" {
  description = "The service account key for file operations"
  value       = google_service_account_key.key.private_key
  sensitive   = true
}