import json
import os
from typing import Dict, List

from openai import OpenAI


def list_files(directory_path: str, file_type: str = "txt") -> List[str]:
    """
    List all files of a specific type in the given directory.

    Args:
    directory_path (str): The path to the directory from which files are listed.
    file_type (str): The type of files to list. Defaults to "txt".

    Returns:
    List[str]: A sorted list of file paths matching the given file type.
    """
    if not os.path.isdir(directory_path):
        raise ValueError(f"Invalid directory path: {directory_path}")

    files = [
        os.path.join(directory_path, file)
        for file in os.listdir(directory_path)
        if file.endswith(f".{file_type}")
    ]

    return sorted(files)


def read_file_content(file_path: str) -> str:
    """Read and return the content of a file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def read_json_file(file_path: str) -> Dict:
    """Read and return the content of a JSON file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_summary_as_json(content, file_path):
    """Save the summary as a JSON file."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(json.loads(content), f, ensure_ascii=False)


def generate_summary(summary_schema: str, transcript: str, client: OpenAI) -> str:
    """Generate a structured summary of the given transcript."""

    system_prompt = "You are an AI practitioner and an expert in explaining concepts to a professional audience."

    user_prompt = f"""
    Objective:
    Given the podcast episode transcript provided, generate a structured summary in JSON format. The summary should include the sections outlined in instructions, adhering strictly to the structure and examples provided in the output section. Always read all the relevant paragraphs before summarizing or identifying key passages.

    Instructions:
    1. Metadata: Include the title, date, and participants of the podcast.
    2. Summary: A concise overview of the podcast transcript.
    3. Topics: A list of the main topics of the discussion.
    4. Quotes: A list of quotes that are exemplary of the discussion. Ensure these quotes are directly cited without paraphrasing, and include the name of the speaker for each quote.
    5. Terms: Identify the key terms that are pivotal to understanding the discussion. Provide definitions for these terms.
    6. Recommendations: A list of suggestions or advice given during the episode.
    7. Conclusions: A summarizing statement that encapsulates the key outcomes or messages of the episode.

    Output:
    Ensure the information is formatted in JSON with the following schema:
    {summary_schema}

    Here is the transcript:
    {transcript}
    """
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


def combine_terms(terms_dict, new_terms):
    for key, value in new_terms.items():
        if key in terms_dict:
            terms_dict[key] = f"{terms_dict[key]} / {value}"
        else:
            terms_dict[key] = value


def generate_final_summary(
    summary_schema: str, combined_summary: str, client: OpenAI
) -> str:
    """Generate a final summary of the combined summaries."""

    system_prompt = "You are an AI practitioner and an expert in explaining concepts to a professional audience."

    user_prompt = f"""
    Objective:
    Given the podcast episode transcript provided, generate a structured summary in JSON format. The summary should include the sections outlined in instructions, adhering strictly to the structure and examples provided in the output section. Always read all the relevant paragraphs before summarizing or identifying key passages.

    Instructions:
    1. Metadata: Include the title, date, and participants of the podcast.
    2. Summary: Summarize the summaries in a single comprehensive statement. Focus on the overarching themes.
    3. Topics: List the five main topics discussed. Read all the topics before picking the five most important ones.
    4. Quotes: Identify the three most important quotes. Read all the quotes before picking the three most important ones. Ensure these quotes are directly cited without paraphrasing, and include the name of the speaker for each quote.
    5. Terms: Identify the key terms that are pivotal to understanding the discussion. Provide definitions for these terms. 
    6. Recommendations: List the five most critical recommendations. 
    7. Conclusions: Summarize the final conclusions in a single statement. This should reflect the implications of the discussion for future AI research and practices. 

    Output:
    Ensure the information is formatted in JSON with the following schema:
    {summary_schema}

    Here are the combined summaries:
    {combined_summary}
    """

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
    summary_schema = read_json_file("summary_schema.json")
    # 1. Process the individual transcripts
    transcript_file_paths = list_files("../data/transcripts/preprocessed")
    for fp in transcript_file_paths:
        # read transcripts
        transcript = read_file_content(fp)

        # summarize the transcripts
        summary = generate_summary(transcript, client)
        # save the transcripts as json
        file_name = os.path.basename(fp).replace(".txt", ".json")
        file_dir = "../data/summaries"
        save_summary_as_json(summary, os.path.join(file_dir, file_name))

    # 2. Combine the summaries
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

    # 3. Generate the final summary
    combined_json = read_json_file("../data/summaries/combined_podcast_data.json")

    final_summary = generate_final_summary(combined_json, client)

    save_summary_as_json(final_summary, "../data/summaries/final_summary.json")
