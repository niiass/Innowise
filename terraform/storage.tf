resource "google_storage_bucket" "weather_lake" {
  name                        = "${var.project_id}-${var.environment}-weather-lake"
  location                    = var.region
  force_destroy               = var.allow_destructive_teardown
  uniform_bucket_level_access = true

  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }

  depends_on = [google_project_service.required]
}
