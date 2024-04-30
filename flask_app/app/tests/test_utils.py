import json
from unittest.mock import Mock
import pytest
from google.cloud import storage

from app.utils import list_files, load_summaries, load_summary_by_id


@pytest.fixture
def mock_storage(monkeypatch):
    mock_client = Mock()
    mock_bucket = Mock()
    mock_blob = Mock()

    # Patch the storage client to use the mock
    monkeypatch.setattr(storage, "Client", lambda: mock_client)
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob

    return mock_bucket, mock_blob


def test_load_summaries_single_file(mock_storage):
    mock_bucket, mock_blob = mock_storage
    mock_blob.download_as_text.return_value = json.dumps({"key": "value"})

    result = load_summaries("test-bucket", ["file1.json"])
    assert result == [{"key": "value"}]
    mock_bucket.blob.assert_called_once_with("file1.json")


def test_load_summaries_multiple_files(mock_storage):
    mock_bucket, mock_blob = mock_storage
    texts = [json.dumps({"key": f"value{i}"}) for i in range(3)]
    mock_blob.download_as_text.side_effect = texts

    result = load_summaries("test-bucket", ["file1.json", "file2.json", "file3.json"])
    assert result == [{"key": "value0"}, {"key": "value1"}, {"key": "value2"}]
    assert mock_bucket.blob.call_count == 3


def test_load_summary_by_id(mock_storage):
    mock_bucket, mock_blob = mock_storage
    mock_blob.download_as_text.return_value = json.dumps(
        {"id": "123", "content": "example"}
    )

    result = load_summary_by_id("test-bucket", "prefix/", "123")
    assert result == {"id": "123", "content": "example"}
    mock_bucket.blob.assert_called_once_with("prefix/123.json")
