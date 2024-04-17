import json
import os
from typing import Dict, List

import yaml
from openai import OpenAI

# TODO: skip transcripts if already done
# TODO: load variables at the top of the file
# TODO: unit tests for all functions


def list_files(directory_path: str, file_type: str = "txt") -> List[str]:
    """List all files of a specific type in the given directory and sorts it by name."""
    if not os.path.isdir(directory_path):
        raise ValueError(f"Invalid directory path: {directory_path}")

    files = [
        os.path.join(directory_path, file)
        for file in os.listdir(directory_path)
        if file.endswith(f".{file_type}")
    ]

    return sorted(files)


# TODO: combine read/load functions
def read_file_content(file_path: str) -> str:
    """Read and return the content of a file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def read_json_file(file_path: str) -> Dict:
    """Read and return the content of a JSON file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_prompts(file_path):
    with open(file_path, "r") as file:
        prompts = yaml.safe_load(file)
    return prompts


def save_summary_as_json(content, file_path):
    """Save the summary as a JSON file."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(json.loads(content), f, ensure_ascii=False)


# TODO: this is overkill, try to simplify (pick one/first term definition)
def combine_terms(terms_dict, new_terms):
    for key, value in new_terms.items():
        if key in terms_dict:
            terms_dict[key] = f"{terms_dict[key]} / {value}"
        else:
            terms_dict[key] = value


# TODO: parametrized model -> use GPT-4 in final summary
def generate_summary(client: OpenAI, system_prompt: str, user_prompt: str) -> str:
    """Generate a summary using the OpenAI API."""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0.5,
        max_tokens=1000,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    client = OpenAI()
    # TODO: load all configuration at the top of the file with a function
    schema = read_file_content("summary_schema.json")
    prompts = load_prompts("prompts.yml")
    system_prompt = prompts["system_prompt"]
    # 1. Process the individual transcripts -> TODO: needs to be a function
    transcript_file_paths = list_files("../data/transcripts/preprocessed")
    for fp in transcript_file_paths:
        # read transcripts
        content = read_file_content(fp)
        prompt_chunks = prompts["user_prompt_chunks"].format(
            schema=schema, content=content
        )
        # summarize the transcripts
        summary = generate_summary(
            client, system_prompt=system_prompt, user_prompt=prompt_chunks
        )
        # save the transcripts as json
        file_name = os.path.basename(fp).replace(".txt", ".json")
        file_dir = "../data/summaries"
        save_summary_as_json(summary, os.path.join(file_dir, file_name))

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

    with open("../data/summaries/combined_podcast_data.json", "w") as outfile:
        json.dump(combined_data, outfile, ensure_ascii=False, indent=4)

    # 3. Generate the final summary -> TODO: simplify
    final_content = read_file_content("../data/summaries/combined_podcast_data.json")
    user_prompt_final = prompts["user_prompt_final"].format(
        schema=schema, content=final_content
    )
    final_summary = generate_summary(
        client, system_prompt=system_prompt, user_prompt=user_prompt_final
    )

    save_summary_as_json(final_summary, "../data/summaries/final_summary.json")
