import json
import math
import os
from typing import Any, Dict, List, Tuple

import yaml
from openai import OpenAI

# TODO: add preprocessing step here
# TODO: skip transcripts if already summarized
# TODO: unit tests for all functions
# TODO: should i put the schema inside the system prompt?

BASE_DATA_DIR = "../data"
TRANSCRIPTS_DIR = os.path.join(BASE_DATA_DIR, "transcripts")
SUMMARIES_DIR = os.path.join(BASE_DATA_DIR, "summaries")

CHUNK_MODEL = "gpt-3.5-turbo-0125"
FINAL_MODEL = "gpt-3.5-turbo-0125"


def list_files(directory_path: str, file_type: str = "txt") -> List[str]:
    """Retrieve and return a sorted list of filenames in a specified directory that match a given file extension."""
    if not os.path.isdir(directory_path):
        raise ValueError(f"Invalid directory path: {directory_path}")
    files = [
        os.path.join(directory_path, file)
        for file in os.listdir(directory_path)
        if file.endswith(f".{file_type}")
    ]
    return sorted(files)


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


def balance_splits(transcript, estimated_parts):
    """Adjust split points to balance transcript across parts."""
    part_starts = [0]
    step_size = len(transcript) // estimated_parts
    for i in range(1, estimated_parts):
        part_end_index = part_starts[-1] + step_size
        part_end = (
            transcript.find("\n", part_end_index) + 1
            if "\n" in transcript[part_end_index:]
            else len(transcript)
        )
        part_starts.append(part_end)
    part_starts.append(len(transcript))
    return part_starts


def split_transcript(transcript, max_chars=56000):
    """Split the transcript into chunks, balancing them more evenly."""
    estimated_parts = math.ceil(len(transcript) / max_chars)
    part_starts = balance_splits(transcript, estimated_parts)
    return [
        transcript[start:end] for start, end in zip(part_starts[:-1], part_starts[1:])
    ]


def load_config(schema_path: str, prompts_path: str) -> Tuple[Any, Any]:
    """Load configuration files for the schema and prompts."""
    schema = read_text("summary_schema.json")
    prompts = load_yaml("prompts.yml")
    return schema, prompts


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


def generate_prompt(prompt_template: str, schema: dict, content: str) -> str:
    """gens a prompt using the provided schema and content."""
    return prompt_template.format(schema=schema, content=content)


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


###############################################################################

schema, prompts = load_config("sum_schema.json", "prompts.yml")
system_prompt = prompts["system_prompt"]
client = OpenAI()

# 1. Load transcript and split into chunks
transcript = read_text(os.path.join(TRANSCRIPTS_DIR, "dwarkesh_podcast_180424.txt"))
chunks = split_transcript(transcript)

# 2. Summarize the chunks
chunk_summaries = []

# TODO: validate the json/dict structure of the summaries
for chunk in chunks:
    chunk_prompt = generate_prompt(prompts["user_prompt_chunks"], schema, chunk)
    chunk_sum = generate_summary(client, system_prompt, chunk_prompt, CHUNK_MODEL)
    chunk_sum_dict = json.loads(chunk_sum)
    chunk_summaries.append(chunk_sum_dict)

# 3. Combine the summaries
combined_summaries = combine_summaries(chunk_summaries)

# 4. Generate the final summary
combined_summaries_txt = json.dumps(combined_summaries)

user_prompt_final = generate_prompt(
    prompts["user_prompt_final"], schema, combined_summaries_txt
)

final_sum = generate_summary(client, system_prompt, user_prompt_final, FINAL_MODEL)

final_sum_dict = json.loads(final_sum)

write_json(final_sum_dict, "../data/summaries/final_sum.json")
