# CockroachDB
resource "cockroach_cluster" "main" {
  name           = "basic-cluster"
  cloud_provider = "GCP"
  plan           = "BASIC"
  serverless     = {}
  regions = [{
    name = "europe-west1"
  }]
  delete_protection = true
}

resource "cockroach_database" "nyt_db" {
  name       = "nyt_data"
  cluster_id = cockroach_cluster.main.id
}

resource "random_password" "sql_user_password" {
  length      = 12
  special     = false
  min_upper   = 2
  min_lower   = 2
  min_numeric = 2
}

resource "cockroach_sql_user" "app_user" {
  name       = "data-load-user"
  password   = random_password.sql_user_password.result
  cluster_id = cockroach_cluster.main.id
}

data "cockroach_connection_string" "db_conn_string" {
  id       = cockroach_cluster.main.id
  sql_user = cockroach_sql_user.app_user.name
  password = cockroach_sql_user.app_user.password
  database = cockroach_database.nyt_db.name
}

# Redis
resource "upstash_redis_database" "cache_db" {
  database_name  = "nyt-cache"
  region         = "global"
  primary_region = "eu-west-1"
  tls            = "true"
  eviction       = true
}