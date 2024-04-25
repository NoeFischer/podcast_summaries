import json
import math
import os
from typing import Any, Dict, List

import yaml
from openai import OpenAI


def list_files(directory_path: str, file_type: str = "txt") -> List[str]:
    """Retrieve and return a sorted list of filenames in a specified directory that match a given file extension."""
    files = [
        os.path.join(directory_path, file)
        for file in os.listdir(directory_path)
        if file.endswith(f".{file_type}")
    ]
    return sorted(files)


def find_unsummarized_transcripts(
    transcripts_dir: str, summaries_dir: str
) -> List[str]:
    transcript_files = list_files(transcripts_dir, "txt")
    summary_files = list_files(summaries_dir, "json")

    transcript_base_names = set(
        os.path.splitext(os.path.basename(file))[0] for file in transcript_files
    )
    summary_base_names = set(
        os.path.splitext(os.path.basename(file))[0] for file in summary_files
    )

    untranslated = transcript_base_names - summary_base_names

    untranslated_paths = [
        os.path.join(transcripts_dir, base_name + ".txt") for base_name in untranslated
    ]

    return untranslated_paths


def load_json(file_path: str):
    """Reads and returns the contents of a JSON file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_yaml(file_path: str):
    """Reads a YAML file from the given file path and returns its content."""
    with open(file_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def read_text(file_path: str) -> str:
    """Reads a plain text file and returns its content as a string."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def write_json(content: Any, file_path: str):
    """Writes the provided content to a JSON file at the specified file path."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=4)


def split_transcript(transcript: str, max_chars: int = 56000) -> list:
    chunks = []
    start = 0
    length = len(transcript)

    delimiters = ["\n\n", ". ", " "]
    buffer_size = min(1000, int(max_chars * 0.1))

    while start < length:
        end = start + max_chars
        buffer_end = min(length, end + buffer_size)

        if end < length:
            split_index = -1
            for delimiter in delimiters:
                split_index = transcript.rfind(delimiter, start, buffer_end)
                if split_index != -1:
                    end = split_index + 1 if delimiter == " " else split_index + 2
                    break
            if split_index == -1:
                end = start + max_chars
        chunks.append(transcript[start:end])
        start = end

    return chunks


def generate_summary(
    client: OpenAI, system_prompt: str, user_prompt: str, model: str
) -> str:
    """Generates a summary based on system and user prompts using the specified OpenAI model."""
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.5,
        max_tokens=1000,
    )
    return response.choices[0].message.content


def combine_summaries(chunk_summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Combines summaries from multiple chunks into a single summary file."""
    combined_sum = chunk_summaries[0]

    for key in ["summary", "conclusions"]:
        combined_sum[key] = [combined_sum[key]]

    operations = {
        "summary": "append",
        "topics": "extend",
        "quotes": "extend",
        "recommendations": "extend",
        "conclusions": "append",
    }

    for chunk_sum in chunk_summaries[1:]:
        for key, operation in operations.items():
            if operation == "append":
                combined_sum[key].append(chunk_sum[key])
            elif operation == "extend":
                combined_sum[key].extend(chunk_sum[key])

        for term, description in chunk_sum["terms"].items():
            if term not in combined_sum["terms"]:
                combined_sum["terms"][term] = description

    return combined_sum


def get_metadata_from_path(transcript_path: str) -> Dict[str, str]:
    """
    Extract the "id" and "podcast" metadata from the transcript file path.

    Args:
        transcript_path (str): The path to the transcript file.

    Returns:
        Dict[str, str]: A dictionary containing the "id" and "podcast" metadata.
    """
    transcript_filename = os.path.basename(transcript_path)
    transcript_name, _ = os.path.splitext(transcript_filename)
    id_value = transcript_name

    podcast_name_parts = transcript_name.split("_")
    podcast_name = " ".join(podcast_name_parts[:-1]).title()

    return {
        "id": id_value,
        "podcast": podcast_name,
    }
