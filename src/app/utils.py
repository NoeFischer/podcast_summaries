# TODO: Implement logging -> replace print statements with logging

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import yaml


def load_config():
    with open("config.yml", "r") as stream:
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


def list_files(directory_path: str) -> List[str]:
    """Retrieve a list of full file paths for .json files in the specified directory."""
    if not os.path.isdir(directory_path):
        raise ValueError(f"Invalid directory path: {directory_path}")
    return [
        os.path.join(directory_path, file)
        for file in os.listdir(directory_path)
        if file.endswith(".json")
    ]


def load_summaries(
    file_paths: List[str], query: str = None, podcast_filter: str = None
) -> List[dict[str, Any]]:
    """Load summary files given by file_paths, convert dates, and return summaries sorted by date in descending order."""
    summaries = []
    for file_path in file_paths:
        with open(file_path, "r") as file:
            summary = json.load(file)
            if podcast_filter and summary["metadata"]["podcast"] != podcast_filter:
                continue
            if query and query.lower() not in summary["metadata"]["title"].lower():
                continue
            summary["metadata"]["date"] = convert_date(summary["metadata"]["date"])
            summaries.append(summary)
    summaries.sort(key=lambda x: x["metadata"]["date"], reverse=True)
    return summaries


def load_summary_by_id(directory_path: str, summary_id: str) -> Optional[Dict]:
    """Load a summary by its ID from the summaries directory."""
    file_path = os.path.join(directory_path, f"{summary_id}.json")
    if not os.path.isfile(file_path):
        return None
    with open(file_path, "r") as file:
        summary = json.load(file)
        summary["metadata"]["date"] = convert_date(summary["metadata"]["date"])
        return summary
