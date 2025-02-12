variable "nyt_api_key" {
  description = "API key for authenticating requests to the New York Times API."
  type        = string
  sensitive   = true
}

variable "project_id" {
  description = "The Google Cloud Project ID where resources will be created."
  type        = string
}

variable "upstash_email" {
  description = "Email address associated with the Upstash account."
  type        = string
  sensitive   = true
}

variable "upstash_api_key" {
  description = "API key for authenticating requests to Upstash Redis services."
  type        = string
  sensitive   = true
}

variable "cockroach_api_key" {
  description = "API key for authenticating requests to CockroachDB."
  type        = string
  sensitive   = true
}