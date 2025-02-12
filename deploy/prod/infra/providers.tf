terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.19.0"
    }
    upstash = {
      source  = "upstash/upstash"
      version = "1.5.3"
    }
    cockroach = {
      source  = "cockroachdb/cockroach"
      version = "1.11.2"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.6.3"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = "europe-west1"
}

provider "upstash" {
  email   = var.upstash_email
  api_key = var.upstash_api_key
}

provider "cockroach" {
  apikey = var.cockroach_api_key
}