from datetime import datetime, timedelta, timezone
import json
import logging

import pandas as pd

from airflow.decorators import dag, task
from airflow.exceptions import AirflowException
from airflow.models.param import Param
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator

BUCKET_NAME = "weather-data-pipeline-506613-dev-weather-lake"
DATASET_ID = "weather_data"
TABLE_ID = "weather_realtime"

# Numeric metric fields as they appear in the tomorrow.io payload -> gold column name
NUMERIC_FIELDS = {
    "temperature": "weather_temperature",
    "humidity": "weather_humidity",
    "windSpeed": "weather_windSpeed",
    "cloudCover": "weather_cloudCover",
    "precipitationProbability": "weather_precipitationProbability",
}

# (min, max) inclusive ranges, only enforced when the field is present
VALUE_RANGES = {
    "temperature": (-90, 70),
    "humidity": (0, 100),
    "windSpeed": (0, 150),
    "cloudCover": (0, 100),
    "precipitationProbability": (0, 100),
}

GOLD_SCHEMA_FIELDS = [
    {"name": "source_object", "type": "STRING", "mode": "REQUIRED"},
    {"name": "event_time", "type": "TIMESTAMP", "mode": "REQUIRED"},
    {"name": "location_name", "type": "STRING", "mode": "REQUIRED"},
    {"name": "location_lat", "type": "FLOAT", "mode": "NULLABLE"},
    {"name": "location_lon", "type": "FLOAT", "mode": "NULLABLE"},
    {"name": "location_type", "type": "STRING", "mode": "NULLABLE"},
    {"name": "ingested_at_utc", "type": "TIMESTAMP", "mode": "REQUIRED"},
    {"name": "weather_temperature", "type": "FLOAT", "mode": "NULLABLE"},
    {"name": "weather_humidity", "type": "FLOAT", "mode": "NULLABLE"},
    {"name": "weather_windSpeed", "type": "FLOAT", "mode": "NULLABLE"},
    {"name": "weather_cloudCover", "type": "FLOAT", "mode": "NULLABLE"},
    {"name": "weather_precipitationProbability", "type": "FLOAT", "mode": "NULLABLE"},
]

CSV_COLUMN_ORDER = [f["name"] for f in GOLD_SCHEMA_FIELDS]


@dag(
    dag_id="weather_silver_processing",
    schedule=None,
    start_date=datetime(2026, 8, 31, tzinfo=timezone.utc),
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "nia",
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
    },
    params={
        "source_path": Param(
            default=None,
            type=["null", "string"],
            description=(
                "Optional Bronze GCS prefix, matching the ingestion function's layout "
                "(e.g. bronze/2026/08/31/13/). If empty, defaults to the previous UTC hour."
            ),
        )
    },
    description="Batch process & validate Bronze JSONs to Silver CSV and BigQuery Gold using TaskFlow API",
)
def weather_pipeline():

    @task
    def process_and_validate_bronze_to_silver(**context) -> str:
        gcs_hook = GCSHook()
        dag_run_conf = context.get("dag_run").conf if context.get("dag_run") else {}
        params = context.get("params", {})

        source_path = dag_run_conf.get("source_path") or params.get("source_path")

        if source_path:
            bronze_prefix = source_path.strip("/") + "/"
            target_dt = datetime.now(timezone.utc)
        else:
            target_dt = datetime.now(timezone.utc) - timedelta(hours=1)
            # NOTE: this must mirror the exact path the Cloud Function writes to:
            # bronze/{YYYY/MM/DD/HH}/weather_{location}_{timestamp}.json
            bronze_prefix = f"bronze/{target_dt.strftime('%Y/%m/%d/%H')}/"

        logging.info(f"Scanning Bronze prefix: gs://{BUCKET_NAME}/{bronze_prefix}")

        file_list = [
            f for f in gcs_hook.list(bucket_name=BUCKET_NAME, prefix=bronze_prefix)
            if f.endswith(".json")
        ]

        if not file_list:
            raise AirflowException(
                f"No Bronze JSON files found at prefix: gs://{BUCKET_NAME}/{bronze_prefix}"
            )

        run_ts_dt = datetime.now(timezone.utc)
        ingested_at_utc = run_ts_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        valid_records = []
        invalid_count = 0

        for blob_name in file_list:
            try:
                file_bytes = gcs_hook.download(bucket_name=BUCKET_NAME, object_name=blob_name)
                payload = json.loads(file_bytes.decode("utf-8"))
            except Exception as e:
                logging.warning(f"Dropping {blob_name}: unreadable/invalid JSON ({e}).")
                invalid_count += 1
                continue

            data_section = payload.get("data")
            location_section = payload.get("location")

            if not isinstance(data_section, dict):
                logging.warning(f"Dropping {blob_name}: 'data' section missing or not a dict.")
                invalid_count += 1
                continue

            if not isinstance(location_section, dict):
                logging.warning(f"Dropping {blob_name}: 'location' section missing or not a dict.")
                invalid_count += 1
                continue

            values = data_section.get("values")
            if not isinstance(values, dict):
                logging.warning(f"Dropping {blob_name}: 'data.values' missing or not a dict.")
                invalid_count += 1
                continue

            event_time = data_section.get("time")
            location_name = location_section.get("name")

            if not event_time or not location_name:
                logging.warning(
                    f"Dropping {blob_name}: missing mandatory event_time or location_name."
                )
                invalid_count += 1
                continue

            # Type + range validation on numeric metric fields
            record_valid = True
            metrics = {}
            for src_field, gold_col in NUMERIC_FIELDS.items():
                val = values.get(src_field)
                if val is None:
                    metrics[gold_col] = None
                    continue
                if not isinstance(val, (int, float)) or isinstance(val, bool):
                    logging.warning(
                        f"Dropping {blob_name}: field '{src_field}' is not numeric ({val!r})."
                    )
                    record_valid = False
                    break
                lo, hi = VALUE_RANGES[src_field]
                if not (lo <= val <= hi):
                    logging.warning(
                        f"Dropping {blob_name}: field '{src_field}' out of range "
                        f"({val}, expected [{lo}, {hi}])."
                    )
                    record_valid = False
                    break
                metrics[gold_col] = val

            if not record_valid:
                invalid_count += 1
                continue

            record = {
                "source_object": blob_name,
                "event_time": event_time,
                "location_name": location_name,
                "location_lat": location_section.get("lat"),
                "location_lon": location_section.get("lon"),
                "location_type": location_section.get("type"),
                "ingested_at_utc": ingested_at_utc,
                **metrics,
            }
            valid_records.append(record)

        if not valid_records:
            raise AirflowException(
                f"Zero valid records remained after validation checks "
                f"({invalid_count} record(s) dropped)."
            )

        df = pd.DataFrame(valid_records)

        # Normalize event_time to a BigQuery-friendly ISO8601 UTC timestamp
        df["event_time"] = pd.to_datetime(df["event_time"], utc=True).dt.strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )

        before = len(df)
        df = df.drop_duplicates(subset=["location_name", "event_time"], keep="last")
        deduped = before - len(df)
        if deduped:
            logging.info(f"Removed {deduped} duplicate record(s) on (location_name, event_time).")

        df = df[CSV_COLUMN_ORDER]

        run_ts = run_ts_dt.strftime("%Y%m%d_%H%M%S")
        # Use the actual hour scanned (works whether source_path was overridden or not)
        hour_from_prefix = bronze_prefix.strip("/").split("/", 1)[1] if source_path else target_dt.strftime("%Y/%m/%d/%H")
        silver_blob_path = f"silver/weather/realtime/{hour_from_prefix}/{run_ts}.csv"

        csv_data = df.to_csv(index=False)
        gcs_hook.upload(
            bucket_name=BUCKET_NAME,
            object_name=silver_blob_path,
            data=csv_data,
            mime_type="text/csv",
        )

        logging.info(
            f"Loaded {len(df)} validated rows ({invalid_count} dropped) to "
            f"gs://{BUCKET_NAME}/{silver_blob_path}"
        )

        return silver_blob_path

    silver_gcs_file = process_and_validate_bronze_to_silver()

    load_to_bigquery_gold = GCSToBigQueryOperator(
        task_id="load_silver_csv_to_bigquery_gold",
        bucket=BUCKET_NAME,
        source_objects=[silver_gcs_file],
        destination_project_dataset_table=f"{DATASET_ID}.{TABLE_ID}",
        schema_fields=GOLD_SCHEMA_FIELDS,
        write_disposition="WRITE_APPEND",
        source_format="CSV",
        skip_leading_rows=1,
        autodetect=False,
    )

    silver_gcs_file >> load_to_bigquery_gold


weather_dag = weather_pipeline()