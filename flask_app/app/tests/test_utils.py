from unittest.mock import Mock, patch

import pytest

from app.utils import convert_date, list_files, load_summaries, load_summary_by_id


class MockBlob:
    """Mock GCS blob storage"""

    def __init__(self, name):
        self.name = name


@pytest.fixture
def config():
    return {"bucket_name": "ai-podcast-cards", "prefix": "summaries/"}


@pytest.mark.parametrize(
    "input, expected",
    [
        ("03-01-2023", "2023-01-03"),
        ("2023-12-03", "2023-12-03"),
        (None, None),
        ("", ""),
        ("29-02-2022", "29-02-2022"),
    ],
)
def test_convert_date(input, expected):
    assert convert_date(input) == expected


@patch("app.utils.storage.Client")
@pytest.mark.parametrize(
    "blobs, expected",
    [
        ([MockBlob("file1.json"), MockBlob("image1.png")], ["file1.json"]),
        (
            [MockBlob("file1.json"), MockBlob("file2.json")],
            ["file1.json", "file2.json"],
        ),
        ([], []),
        ([MockBlob("image1.png"), MockBlob("document.txt")], []),
    ],
)
def test_list_files(MockClient, config, blobs, expected):
    # Arrange
    bucket_mock = Mock()
    MockClient.return_value.bucket.return_value = bucket_mock

    blobs = [MockBlob("file1.json"), MockBlob("image1.png")]
    bucket_mock.list_blobs.return_value = blobs

    # Act
    files = list_files(config["bucket_name"], config["prefix"])

    # Assert
    assert files == ["file1.json"]


@patch("app.utils.storage.Client")
@pytest.mark.parametrize(
    "file_paths, input_summaries, expected_summaries",
    [
        (
            ["summaries/summary1.json"],
            ['{"summary": "Summary Podcast 1"}'],
            [{"summary": "Summary Podcast 1"}],
        ),
        (
            ["summaries/summary1.json", "summaries/summary2.json"],
            ['{"summary": "Summary Podcast 1"}', '{"summary": "Summary Podcast 2"}'],
            [{"summary": "Summary Podcast 1"}, {"summary": "Summary Podcast 2"}],
        ),
    ],
)
def test_load_summaries(
    MockClient, config, file_paths, input_summaries, expected_summaries
):
    # Arrange
    mock_bucket = Mock()
    MockClient.return_value.bucket.return_value = mock_bucket

    mock_blobs = []
    for summary in input_summaries:
        mock_blob = Mock()
        mock_blob.download_as_text.return_value = summary
        mock_blobs.append(mock_blob)

    mock_bucket.blob.side_effect = lambda path: mock_blobs[file_paths.index(path)]

    # Act
    summaries = load_summaries(config["bucket_name"], file_paths)

    # Assert
    assert summaries == expected_summaries


@patch("app.utils.storage.Client")
@pytest.mark.parametrize(
    "summary_id, input_summary, expected_summary",
    [
        (
            "dwarkesh_podcast_230327",
            '{"summary": "Summary Podcast 1"}',
            {"summary": "Summary Podcast 1"},
        ),
        ("12345", '{"summary": "Summary Podcast 2"}', {"summary": "Summary Podcast 2"}),
        (
            "special_@#$_233",
            '{"summary": "Unique Summary"}',
            {"summary": "Unique Summary"},
        ),
        (
            "long_complex_id_9876543210_with_more_details",
            '{"summary": "Detailed Summary"}',
            {"summary": "Detailed Summary"},
        ),
    ],
)
def test_load_summaries_by_id(
    MockClient, config, summary_id, input_summary, expected_summary
):
    # Arrange
    file_path = f"{config["prefix"]}{summary_id}.json"

    mock_bucket = Mock()
    MockClient.return_value.bucket.return_value = mock_bucket

    mock_blob = Mock()
    mock_bucket.blob.return_value = mock_blob

    mock_blob.download_as_text.return_value = input_summary

    # Act
    summary = load_summary_by_id(config["bucket_name"], config["prefix"], summary_id)

    # Assert
    mock_bucket.blob.assert_called_once_with(file_path)
    assert summary == expected_summary
