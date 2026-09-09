output "weather_lake_bucket_name" {
  description = "GCS bucket holding the bronze/silver layers"
  value       = google_storage_bucket.weather_lake.name
}

output "bigquery_dataset_id" {
  description = "BigQuery dataset holding the gold table"
  value       = google_bigquery_dataset.weather_dataset.dataset_id
}

output "bigquery_table_id" {
  description = "Fully-qualified BigQuery gold table"
  value       = "${var.project_id}.${google_bigquery_dataset.weather_dataset.dataset_id}.${google_bigquery_table.weather_gold_table.table_id}"
}

output "cloud_function_name" {
  description = "Deployed Cloud Function (Gen2) name"
  value       = google_cloudfunctions2_function.weather_bronze_ingestion.name
}

output "cloud_function_url" {
  description = "HTTPS URL of the ingestion function"
  value       = google_cloudfunctions2_function.weather_bronze_ingestion.url
}

output "cloud_scheduler_job_name" {
  description = "Cloud Scheduler job triggering ingestion every 10 minutes"
  value       = google_cloud_scheduler_job.weather_ingestion_trigger.name
}

output "cloud_function_service_account_email" {
  description = "Service account the ingestion function runs as"
  value       = google_service_account.sa_cloud_function.email
}

output "scheduler_service_account_email" {
  description = "Service account Cloud Scheduler uses to invoke the function"
  value       = google_service_account.sa_scheduler.email
}

output "airflow_service_account_email" {
  description = "Service account local Airflow uses for GCS/BigQuery access"
  value       = google_service_account.sa_airflow_local.email
}

output "secret_id" {
  description = "Secret Manager secret ID holding the Tomorrow.io API key"
  value       = google_secret_manager_secret.tomorrow_api_key.secret_id
}
