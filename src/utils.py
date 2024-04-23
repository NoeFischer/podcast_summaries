import os
from typing import List


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
