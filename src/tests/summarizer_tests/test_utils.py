import pytest
import os

from unittest.mock import mock_open, patch

from summarizer.utils import (
    list_files,
    find_unsummarized_transcripts,
    load_json,
    load_yaml,
    read_text,
    write_json,
    split_transcript,
)


@pytest.fixture
def setup_environment(tmp_path):
    base_dir = tmp_path / "base"
    transcripts_dir = base_dir / "transcripts"
    summaries_dir = base_dir / "summaries"

    transcripts_dir.mkdir(parents=True)
    summaries_dir.mkdir(parents=True)

    for i in range(1, 4):
        (transcripts_dir / f"transcript_{i}.txt").touch()
        (summaries_dir / f"summary_{i}.json").touch()

    (transcripts_dir / "image.png").touch()

    return transcripts_dir, summaries_dir


@pytest.fixture(
    params=[
        {
            "transcript_files": ["doc1.txt", "doc2.txt", "doc3.txt"],
            "summary_files": ["doc1.json", "doc2.json"],
            "expected": ["doc3.txt"],
        },
        {
            "transcript_files": ["doc1.txt", "doc2.txt"],
            "summary_files": ["doc1.json"],
            "expected": ["doc2.txt"],
        },
        {
            "transcript_files": ["doc1.txt", "doc2.txt", "doc3.txt", "doc4.txt"],
            "summary_files": ["doc1.json", "doc2.json", "doc4.json"],
            "expected": ["doc3.txt"],
        },
    ]
)
def mock_list_files(setup_environment, request):
    transcripts_dir, summaries_dir = setup_environment
    with patch("summarizer.utils.list_files") as mocked_list_files:
        mocked_transcript_files = [
            os.path.join(transcripts_dir, f) for f in request.param["transcript_files"]
        ]
        mocked_summary_files = [
            os.path.join(summaries_dir, f) for f in request.param["summary_files"]
        ]
        mocked_list_files.side_effect = [mocked_transcript_files, mocked_summary_files]
        yield transcripts_dir, summaries_dir, request.param["expected"]


@pytest.mark.parametrize(
    "extension, expected, dir_index",
    [
        (
            "txt",
            ["transcript_1.txt", "transcript_2.txt", "transcript_3.txt"],
            0,
        ),
        (
            "json",
            ["summary_1.json", "summary_2.json", "summary_3.json"],
            1,
        ),
    ],
)
def test_list_files(setup_environment, extension, expected, dir_index):
    transcripts_dir, summaries_dir = setup_environment
    file_dir = (transcripts_dir, summaries_dir)[dir_index]
    result = list_files(file_dir, extension)
    assert result == [str(file_dir / file) for file in expected]


def test_find_unsummarized_transcripts(mock_list_files):
    transcripts_dir, summaries_dir, expected = mock_list_files
    expected_result = [os.path.join(transcripts_dir, f) for f in expected]
    result = find_unsummarized_transcripts(transcripts_dir, summaries_dir)
    assert sorted(result) == sorted(expected_result)


def test_load_json():
    mock_data = '{"name": "John", "age": 30}'
    with patch("builtins.open", mock_open(read_data=mock_data)), patch(
        "json.load"
    ) as mock_json_load:
        load_json("dummy.json")
        mock_json_load.assert_called_once()


def test_load_yaml():
    mock_data = "name: John\nage: 30"
    with patch("builtins.open", mock_open(read_data=mock_data)), patch(
        "yaml.safe_load"
    ) as mock_yaml_load:
        load_yaml("dummy.yaml")
        mock_yaml_load.assert_called_once()


def test_read_text():
    expected_data = "Hello, world!"
    with patch("builtins.open", mock_open(read_data=expected_data)) as mock_file:
        result = read_text("dummy.txt")
        mock_file.assert_called_with("dummy.txt", "r", encoding="utf-8")
        assert result == expected_data


def test_write_json():
    content = {"name": "John", "age": 30}
    with patch("builtins.open", mock_open()) as mock_file:
        with patch("json.dump") as mock_json_dump:
            write_json(content, "dummy.json")
            mock_file.assert_called_with("dummy.json", "w", encoding="utf-8")
            mock_json_dump.assert_called_once_with(
                content, mock_file.return_value, ensure_ascii=False, indent=4
            )


@pytest.mark.parametrize(
    "transcript, max_chars",
    [
        ("", 56000),
        ("First paragraph.\n\nSecond paragraph.\n\nThird paragraph.", 20),
        ("Sentence one. Sentence two. Sentence three.", 25),
        ("Long paragraph without any breaks" * 10, 50),
        ("Paragraph with a very-long-word-" + "a" * 100 + " included.", 100),
    ],
)
def test_split_transcript(transcript, max_chars):
    result = split_transcript(transcript, max_chars)
    for chunk in result:
        assert len(chunk) <= max_chars + 1000, f"Too long: {len(chunk)}"
    if transcript:
        expected_chunks = max(1, len(transcript) // max_chars)
        assert (
            len(result) >= expected_chunks
        ), f"Expected min. {expected_chunks} chunks, got {len(result)}"
