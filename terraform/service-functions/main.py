import os
import json
from datetime import datetime, timezone
import functions_framework
import requests
from google.cloud import secretmanager
from google.cloud import storage

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "weather-data-pipeline-506613")
BUCKET_NAME = os.environ.get("BUCKET_NAME", "weather-data-pipeline-506613-dev-weather-lake")
SECRET_ID = os.environ.get("SECRET_ID", "TOMORROW_API_KEY")
ENV_LOCATION = os.environ.get("WEATHER_LOCATION")

def get_secret(secret_id: str, project_id: str) -> str:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

@functions_framework.http
def weather_bronze_ingestion(request):
    try:
        request_json = request.get_json(silent=True)
        request_args = request.args

        location = None
        if request_args and "location" in request_args:
            location = request_args["location"]
        elif request_json and "location" in request_json:
            location = request_json["location"]
        elif ENV_LOCATION:
            location = ENV_LOCATION

        if not location:
            return (
                json.dumps({"status": "error", "message": "Missing required 'location' parameter or environment variable."}),
                400,
                {"Content-Type": "application/json"}
            )

        api_key = get_secret(SECRET_ID, PROJECT_ID)
        url = f"https://api.tomorrow.io/v4/weather/realtime?location={location}&apikey={api_key}"
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        raw_data = response.json()

        now = datetime.now(timezone.utc)
        timestamp_str = now.strftime("%Y%m%d_%H%M%S")
        safe_location = location.lower().replace(" ", "_").replace(",", "_")
        gcs_blob_path = f"bronze/{now.strftime('%Y/%m/%d/%H')}/weather_{safe_location}_{timestamp_str}.json"

        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(gcs_blob_path)
        
        blob.upload_from_string(
            data=json.dumps(raw_data, indent=2),
            content_type="application/json"
        )

        log_msg = f"Successfully landed payload: gs://{BUCKET_NAME}/{gcs_blob_path}"
        print(log_msg)
        return (
            json.dumps({"status": "success", "location": location, "gcs_path": gcs_blob_path}),
            200,
            {"Content-Type": "application/json"}
        )

    except Exception as e:
        error_msg = f"Ingestion error: {str(e)}"
        print(error_msg)
        return (json.dumps({"status": "error", "message": error_msg}), 500, {"Content-Type": "application/json"})