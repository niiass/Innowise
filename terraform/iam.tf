resource "google_service_account" "sa_cloud_function" {
  account_id   = "sa-cloud-function"
  display_name = "Service Account for Cloud Function Gen2 Ingestion"
}

resource "google_secret_manager_secret_iam_member" "cf_secret_access" {
  secret_id = google_secret_manager_secret.tomorrow_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.sa_cloud_function.email}"
}

resource "google_storage_bucket_iam_member" "cf_storage_writer" {
  bucket = google_storage_bucket.weather_lake.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${google_service_account.sa_cloud_function.email}"
}

resource "google_service_account" "sa_scheduler" {
  account_id   = "sa-scheduler"
  display_name = "Service Account for Cloud Scheduler Invoker"
}

resource "google_service_account" "sa_airflow_local" {
  account_id   = "sa-airflow-local"
  display_name = "Service Account for Local Airflow DAG Executions"
}

resource "google_storage_bucket_iam_member" "airflow_storage_admin" {
  bucket = google_storage_bucket.weather_lake.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.sa_airflow_local.email}"
}

resource "google_bigquery_dataset_iam_member" "airflow_bq_editor" {
  dataset_id = google_bigquery_dataset.weather_dataset.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.sa_airflow_local.email}"
}

resource "google_project_iam_member" "airflow_bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.sa_airflow_local.email}"
}
