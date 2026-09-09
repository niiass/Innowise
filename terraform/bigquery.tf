resource "google_bigquery_dataset" "weather_dataset" {
  dataset_id                 = "weather_data"
  friendly_name              = "Weather Analytics Dataset"
  description                = "Gold layer dataset for realtime weather metrics"
  location                   = var.region
  delete_contents_on_destroy = var.allow_destructive_teardown

  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }

  depends_on = [google_project_service.required]
}

resource "google_bigquery_table" "weather_gold_table" {
  dataset_id          = google_bigquery_dataset.weather_dataset.dataset_id
  table_id            = "weather_realtime"
  deletion_protection = !var.allow_destructive_teardown

  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }

  schema = jsonencode([
    {
      name        = "source_object"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "source path of file from where object came"
    },
    {
      name        = "event_time"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "value from time field"
    },
    {
      name        = "location_name"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "location name"
    },
    {
      name        = "location_lat"
      type        = "FLOAT64"
      mode        = "NULLABLE"
      description = "location latitude"
    },
    {
      name        = "location_lon"
      type        = "FLOAT64"
      mode        = "NULLABLE"
      description = "location longitude"
    },
    {
      name        = "location_type"
      type        = "STRING"
      mode        = "NULLABLE"
      description = "location type"
    },
    {
      name        = "ingested_at_utc"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "timestamp where rows were processed"
    },
    {
      name        = "weather_temperature"
      type        = "FLOAT64"
      mode        = "NULLABLE"
      description = "temperature measurement"
    },
    {
      name        = "weather_humidity"
      type        = "FLOAT64"
      mode        = "NULLABLE"
      description = "humidity percentage"
    },
    {
      name        = "weather_windSpeed"
      type        = "FLOAT64"
      mode        = "NULLABLE"
      description = "wind speed measurement"
    },
    {
      name        = "weather_cloudCover"
      type        = "FLOAT64"
      mode        = "NULLABLE"
      description = "cloud cover percentage"
    },
    {
      name        = "weather_precipitationProbability"
      type        = "FLOAT64"
      mode        = "NULLABLE"
      description = "precipitation probability percentage"
    }
  ])
}
