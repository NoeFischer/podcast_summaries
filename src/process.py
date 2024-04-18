import json
import os
from typing import Any, Callable, List, Optional, Tuple

import yaml
from openai import OpenAI

# TODO: skip transcripts if already summarized
# TODO: unit tests for all functions
# TODO: should i put the schema inside the system prompt?

BASE_DATA_DIR = "../data"
TRANSCRIPTS_DIR = os.path.join(BASE_DATA_DIR, "transcripts")
SUMMARIES_DIR = os.path.join(BASE_DATA_DIR, "summaries")

CHUNK_MODEL = "gpt-3.5-turbo-0125"
FINAL_MODEL = "gpt-4-turbo"


def list_files(directory_path: str, file_type: str = "txt") -> List[str]:
    """
    Retrieve and return a sorted list of filenames in a specified directory that match a given file extension.

    Args:
        directory_path (str): The path of the directory from which to list files.
        file_type (str): The file extension to filter by; defaults to 'txt'. The extension should not include the dot.

    Returns:
        List[str]: A list of fully qualified file paths, sorted alphabetically.

    Raises:
        ValueError: If the specified directory_path does not exist or is not a directory.

    Examples:
        >>> list_files("/path/to/directory", "pdf")
        ['/path/to/directory/file1.pdf', '/path/to/directory/file2.pdf']
    """
    if not os.path.isdir(directory_path):
        raise ValueError(f"Invalid directory path: {directory_path}")

    files = [
        os.path.join(directory_path, file)
        for file in os.listdir(directory_path)
        if file.endswith(f".{file_type}")
    ]

    return sorted(files)


def read_file(file_path: str, loader: Optional[Callable[[Any], Any]] = None) -> Any:
    """
    Read and return the content of a file. If a loader is specified, it is used to parse the file.

    Args:
    - file_path: The path to the file that should be read.
    - loader: A callable that takes a file object and returns the parsed data.
              Common loaders include `json.load` and `yaml.safe_load`.
              If None, the file is read as a plain text.

    Returns:
    - The content of the file either as a string (if no loader is provided) or as parsed data.

    Raises:
    - FileNotFoundError: If the file does not exist.
    - IOError: If the file cannot be opened.
    - Exception: Propagates any exception raised by the loader.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            if loader is not None:
                return loader(file)
            else:
                return file.read()
    except Exception as e:
        raise Exception(f"Failed to read or parse the file {file_path}: {e}")


def write_json(content: Any, file_path: str):
    """
    Writes the provided content to a JSON file at the specified file path.

    The function handles both structured data and serialized JSON strings.
    If the content is a string, it will be parsed into a Python object.

    Args:
    - content: The content to save, either a structured data (e.g., dict, list) or a serialized JSON string.
    - file_path: The path where the JSON file will be saved.

    Raises:
    - TypeError: If the content is a string but not valid JSON, or if the content cannot be serialized into JSON.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        # Automatically parse if content is a string and appears to be JSON
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except json.JSONDecodeError as e:
                raise TypeError(f"Failed to parse content as JSON: {str(e)}")

        # Serialize the content to JSON and write to file
        try:
            json.dump(content, f, ensure_ascii=False, indent=4)
        except TypeError as e:
            raise TypeError(f"Failed to serialize content to JSON: {str(e)}")


def generate_summary(
    client: OpenAI, system_prompt: str, user_prompt: str, model: str
) -> str:
    """
    Generates a summary based on system and user prompts using the specified OpenAI model.

    This function calls the OpenAI API to obtain a summary. It sends a sequence of messages:
    one from the system and one from the user. The model used can be specified.

    Args:
    - client: An instance of the OpenAI client.
    - system_prompt: The initial context or instruction provided by the system.
    - user_prompt: The query or statement from the user that needs summarization.
    - model: The OpenAI model to use for generating the summary.

    Returns:
    - str: The generated summary as a string.
    """

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
    """Generates a prompt using the provided schema and content."""
    return prompt_template.format(schema=schema, content=content)


# TODO: this is overkill, try to simplify (pick one/first term definition)
def combine_terms(terms_dict, new_terms):
    for key, value in new_terms.items():
        if key in terms_dict:
            terms_dict[key] = f"{terms_dict[key]} / {value}"
        else:
            terms_dict[key] = value


def load_config(
    schema_file_path: str, prompts_file_path: str
) -> Tuple[Optional[Any], Optional[Any]]:
    schema = read_file("summary_schema.json")
    prompts = read_file("prompts.yml", yaml.safe_load)
    return schema, prompts


###############################################################################

# Load configuration files
schema, prompts = load_config("summary_schema.json", "prompts.yml")
system_prompt = prompts["system_prompt"]
# Load the OpenAI client
client = OpenAI()

# 1. Process the individual transcripts
for chunk_path in list_files(os.path.join(TRANSCRIPTS_DIR, "preprocessed"), "txt"):
    chunk = read_file(chunk_path)
    chunk_prompt = generate_prompt(prompts["user_prompt_chunks"], schema, chunk)
    chunk_summary = generate_summary(client, system_prompt, chunk_prompt, CHUNK_MODEL)
    summary_file_path = os.path.join(
        SUMMARIES_DIR, os.path.splitext(os.path.basename(chunk_path))[0] + ".json"
    )
    write_json(chunk_summary, summary_file_path)

# 2. Combine the summaries -> TODO: needs to be a function
file_paths = list_files("../data/summaries", "json")

combined_data = {
    "metadata": {},
    "summary": [],
    "topics": [],
    "quotes": [],
    "terms": {},
    "recommendations": [],
    "conclusions": [],
}

metadata_set = False

for file_path in file_paths:
    with open(file_path, "r") as file:
        data = json.load(file)
        if not metadata_set:
            combined_data["metadata"] = data["metadata"]
            metadata_set = True
        combined_data["summary"].append(data["summary"])
        combined_data["topics"].extend(data["topics"])
        combined_data["quotes"].extend(data["quotes"])
        combine_terms(combined_data["terms"], data["terms"])
        combined_data["recommendations"].extend(data["recommendations"])
        combined_data["conclusions"].append(data["conclusions"])

write_json(combined_data, "../data/summaries/combined_podcast_data.json")

# 3. Generate the final summary -> TODO: simplify
final_content = read_file("../data/summaries/combined_podcast_data.json")

user_prompt_final = generate_prompt(prompts["user_prompt_final"], schema, final_content)

final_summary = generate_summary(client, system_prompt, user_prompt_final, FINAL_MODEL)

write_json(final_summary, "../data/summaries/final_summary.json")
