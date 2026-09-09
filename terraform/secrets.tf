resource "google_secret_manager_secret" "tomorrow_api_key" {
  secret_id = "TOMORROW_API_KEY"

  replication {
    auto {}
  }

  labels = {
    environment = var.environment
    managed_by  = "terraform"
  }
}
