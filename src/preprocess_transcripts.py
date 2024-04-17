import math
import os


def read_file_content(file_path):
    """Read and return the content of a file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def write_file_content(file_path, content):
    """Write content to a file."""
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"Created: {file_path}")


def find_next_paragraph_start(content, index):
    """Find the start index of the next paragraph."""
    try:
        return content.index("\n", index) + 1
    except ValueError:  # If no newline is found, return the end of content
        return len(content)


def balance_splits(content, estimated_parts):
    """Adjust split points to balance content across parts."""
    part_starts = [0]
    for _ in range(estimated_parts - 1):
        part_end = find_next_paragraph_start(
            content, part_starts[-1] + len(content) // estimated_parts
        )
        part_starts.append(part_end)
    part_starts.append(
        len(content)
    )  # Ensure the last part goes to the end of the content
    return part_starts


def split_content(content, max_chars=56000):
    """Split the content into chunks, balancing them more evenly."""
    estimated_parts = math.ceil(len(content) / max_chars)
    part_starts = balance_splits(content, estimated_parts)
    return [
        content[part_starts[i] : part_starts[i + 1]]
        for i in range(len(part_starts) - 1)
    ]


def split_text_file(file_path, output_dir=None, max_chars=56000):
    if output_dir is None:
        output_dir = os.path.dirname(file_path)

    content = read_file_content(file_path)
    parts = split_content(content, max_chars)

    base_name = os.path.splitext(os.path.basename(file_path))[0]

    for i, part_content in enumerate(parts, start=1):
        part_file_path = os.path.join(output_dir, f"{base_name}_part_{i}.txt")
        write_file_content(part_file_path, part_content)


if __name__ == "__main__":
    file_path = "../data/transcripts/dwarkesh_podcast_280324.txt"
    split_text_file(file_path)
