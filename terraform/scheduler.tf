resource "google_cloud_scheduler_job" "weather_ingestion_trigger" {
  name        = "weather-bronze-ingestion-trigger"
  description = "Triggers the weather bronze ingestion function every 10 minutes"
  schedule    = "*/10 * * * *"
  time_zone   = "Etc/UTC"
  region      = var.region

  http_target {
    http_method = "POST"
    uri         = google_cloudfunctions2_function.weather_bronze_ingestion.url

    oidc_token {
      service_account_email = google_service_account.sa_scheduler.email
      audience               = google_cloudfunctions2_function.weather_bronze_ingestion.url
    }
  }

  retry_config {
    retry_count = 1
  }

  depends_on = [
    google_project_service.required,
    google_cloudfunctions2_function_iam_member.scheduler_invoker,
    google_cloud_run_service_iam_member.scheduler_run_invoker,
  ]
}
