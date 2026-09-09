data "archive_file" "weather_bronze_ingestion_zip" {
  type        = "zip"
  source_dir  = "${path.module}/service-functions"
  output_path = "${path.module}/.build/weather_bronze_ingestion.zip"
}

# Small, ephemeral bucket that only holds deployable function source zips —
# force_destroy = true is fine here since it never holds pipeline data.
resource "google_storage_bucket" "function_source" {
  name                        = "${var.project_id}-${var.environment}-function-source"
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true

  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }

  depends_on = [google_project_service.required]
}

# Content-addressed object name so a change in source code produces a new
# object and forces the function to redeploy with the new build.
resource "google_storage_bucket_object" "weather_bronze_ingestion_source" {
  name   = "weather_bronze_ingestion/${data.archive_file.weather_bronze_ingestion_zip.output_md5}.zip"
  bucket = google_storage_bucket.function_source.name
  source = data.archive_file.weather_bronze_ingestion_zip.output_path
}

resource "google_cloudfunctions2_function" "weather_bronze_ingestion" {
  name        = "weather-bronze-ingestion"
  location    = var.region
  description = "Fetches current weather from Tomorrow.io and lands the raw payload in the Bronze GCS layer."

  build_config {
    runtime     = "python312"
    entry_point = "weather_bronze_ingestion"

    source {
      storage_source {
        bucket = google_storage_bucket.function_source.name
        object = google_storage_bucket_object.weather_bronze_ingestion_source.name
      }
    }
  }

  service_config {
    max_instance_count    = 1
    min_instance_count    = 0
    available_memory      = "256M"
    timeout_seconds       = 60
    service_account_email = google_service_account.sa_cloud_function.email
    ingress_settings      = "ALLOW_ALL"

    environment_variables = {
      GCP_PROJECT_ID   = var.project_id
      BUCKET_NAME      = google_storage_bucket.weather_lake.name
      SECRET_ID        = google_secret_manager_secret.tomorrow_api_key.secret_id
      WEATHER_LOCATION = var.location_name
    }
  }

  depends_on = [google_project_service.required]
}

# Gen2 functions run on Cloud Run under the hood; this is the invoker
# permission Cloud Scheduler needs to call the function's HTTPS endpoint.
resource "google_cloudfunctions2_function_iam_member" "scheduler_invoker" {
  project        = var.project_id
  location       = var.region
  cloud_function = google_cloudfunctions2_function.weather_bronze_ingestion.name
  role           = "roles/cloudfunctions.invoker"
  member         = "serviceAccount:${google_service_account.sa_scheduler.email}"
}

# Belt-and-suspenders: also grant run.invoker directly on the backing Cloud
# Run service, since some Gen2 setups enforce Cloud Run's own IAM layer.
resource "google_cloud_run_service_iam_member" "scheduler_run_invoker" {
  project  = var.project_id
  location = var.region
  service  = google_cloudfunctions2_function.weather_bronze_ingestion.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.sa_scheduler.email}"
}
