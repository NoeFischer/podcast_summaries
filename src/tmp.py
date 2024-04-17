import os
from typing import List


def list_transcript_files(directory_path: str, file_type: str = "txt") -> List[str]:
    """List all transcript files in the given directory."""
    return sorted(
        [
            os.path.join(directory_path, f)
            for f in os.listdir(directory_path)
            if f.endswith(f".{file_type}")
        ]
    )


transcript_file_paths = list_transcript_files("../data/transcripts/preprocessed")

print(transcript_file_paths)
