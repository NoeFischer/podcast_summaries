import json
import os

from openai import OpenAI
from tqdm import tqdm

from utils import (
    combine_summaries,
    find_unsummarized_transcripts,
    generate_summary,
    get_metadata_from_path,
    load_yaml,
    read_text,
    split_transcript,
    write_json,
)


if __name__ == "__main__":
    # Configuration
    config = load_yaml("config.yml")

    TRANSCRIPTS_DIR = config["paths"]["transcripts"]
    SUMMARIES_DIR = config["paths"]["summaries"]

    CHUNK_MODEL = config["models"]["chunk"]
    COMBINED_MODEL = config["models"]["combined"]

    # Initialize OpenAI client
    client = OpenAI()

    # Generate system prompt
    schema = json.dumps(config["schema"], indent=4)
    system_prompt = config["prompts"]["system"].format(schema=schema)

    # Find untranslated transcripts
    untranslated_paths = find_unsummarized_transcripts(TRANSCRIPTS_DIR, SUMMARIES_DIR)

    # Process transcripts
    if not untranslated_paths:
        print("No transcripts to summarize.")
    else:
        for transcript_path in tqdm(untranslated_paths, desc="Processing Transcripts"):
            print(f"Processing {transcript_path}...")
            # Read transcript and split into chunks
            transcript = read_text(transcript_path)
            chunks = split_transcript(transcript)

            # generate summaries for each chunk
            chunk_summaries = []
            for chunk in chunks:
                chunk_prompt = config["prompts"]["user_chunk"].format(content=chunk)
                chunk_sum = generate_summary(
                    client, system_prompt, chunk_prompt, CHUNK_MODEL
                )
                chunk_sum_dict = json.loads(chunk_sum)
                chunk_summaries.append(chunk_sum_dict)

            # combine summaries into a single file
            combined_summaries = combine_summaries(chunk_summaries)
            combined_summaries_txt = json.dumps(
                combined_summaries, ensure_ascii=False, indent=4
            )

            # generate final summary
            user_prompt_final = config["prompts"]["user_combined"].format(
                content=combined_summaries_txt
            )
            final_sum = generate_summary(
                client, system_prompt, user_prompt_final, COMBINED_MODEL
            )
            final_sum_dict = json.loads(final_sum)
            final_sum_dict["metadata"].update(get_metadata_from_path(transcript_path))

            # write final summary to file
            summary_path = os.path.join(
                SUMMARIES_DIR,
                os.path.basename(transcript_path).replace(".txt", ".json"),
            )
            write_json(final_sum_dict, summary_path)
