# TODO: Implement logging -> replace print statements with logging

import json
from datetime import datetime
from typing import Any, Dict, List

import yaml
from google.cloud import storage


def load_config(file_path: str) -> Dict[str, Any]:
    with open(file_path, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as e:
            print(e)
            return {}


def convert_date(date_str: str) -> str:
    """Convert date strings between two formats or return the original input with a logged warning for invalid formats."""
    if date_str is None or date_str == "":
        print("Date string cannot be empty or None")
        return date_str
    try:
        return datetime.strptime(date_str, "%d-%m-%Y").strftime("%Y-%m-%d")
    except ValueError:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            print(f"Invalid date format for input: {date_str}")
            return date_str


def list_files(bucket_name: str, prefix: str) -> List[str]:
    """List files in a Google Cloud Storage bucket with a given prefix."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    files = [
        blob.name
        for blob in bucket.list_blobs(prefix=prefix)
        if blob.name.endswith(".json")
    ]
    return files


def load_summaries(bucket_name, file_paths):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    summaries = []

    for file_path in file_paths:
        blob = bucket.blob(file_path)
        summary = json.loads(blob.download_as_text())
        summaries.append(summary)

    return summaries


def load_summary_by_id(
    bucket_name: str, prefix: str, summary_id: str
) -> Dict[str, Any]:
    """Load a summary by its ID from Google Cloud Storage within the specified bucket and prefix."""
    if not summary_id:
        raise ValueError("Invalid summary ID provided")

    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    file_name = f"{prefix}{summary_id}.json"
    blob = bucket.blob(file_name)

    json_data = blob.download_as_text()
    summary = json.loads(json_data)
    return summary
