variable "project_id" {
  type        = string
  description = "The GCP Project ID"
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "GCP region for deployment"
}

variable "environment" {
  type        = string
  default     = "dev"
  description = "Target deployment environment"

  validation {
    condition     = contains(["dev", "prod", "staging"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "location_name" {
  type        = string
  default     = "tbilisi"
  description = "Target location for weather data collection"
}

variable "allow_destructive_teardown" {
  type        = bool
  default     = false
  description = <<-EOT
    When false (default), the bucket and BigQuery dataset/table refuse to be
    emptied/deleted by 'terraform destroy' (force_destroy = false,
    delete_contents_on_destroy = false, deletion_protection = true) — this is
    the state-safe default for day-to-day use.
    Set to true only when you intentionally want to tear the whole project
    down, e.g. via `terraform apply -var="allow_destructive_teardown=true"`
    followed by `terraform destroy`.
  EOT
}
