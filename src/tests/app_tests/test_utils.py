import json
import os
from unittest.mock import mock_open, patch

import pytest
from app import utils


@pytest.fixture
def mock_summaries():
    return [
        {"metadata": {"podcast": "Science Friday", "title": "Astrophysics"}},
        {"metadata": {"podcast": "History Extra", "title": "History"}},
        {"metadata": {"podcast": "Science Friday", "title": "Quantum Computing"}},
    ]


def test_load_config_success():
    # Mock data representing a valid YAML content
    yaml_content = """
    database: postgresql
    user: admin
    password: secret
    """
    with patch("builtins.open", mock_open(read_data=yaml_content)):
        config = utils.load_config()

        assert config == {
            "database": "postgresql",
            "user": "admin",
            "password": "secret",
        }


@pytest.mark.parametrize(
    "input_date, expected_output",
    [
        ("12-03-2022", "2022-03-12"),
        ("30-02-2022", "30-02-2022"),
        ("2022-03-12", "2022-03-12"),
        ("12/03/2022", "12/03/2022"),
        ("", ""),
        (None, None),
    ],
)
def test_convert_date(input_date, expected_output):
    assert utils.convert_date(input_date) == expected_output


def test_list_files_with_json_files(tmp_path):
    files = ["file1.json", "file2.txt", "file3.json"]
    expected_paths = sorted(
        [os.path.join(tmp_path, file) for file in files if file.endswith(".json")]
    )
    for file in files:
        (tmp_path / file).touch()
    result = sorted(utils.list_files(str(tmp_path)))
    assert result == expected_paths


@pytest.mark.parametrize(
    "podcast_filter, query, expected_count, expected_titles",
    [
        (None, None, 3, ["Astrophysics", "History", "Quantum Computing"]),
        ("Science Friday", None, 2, ["Astrophysics", "Quantum Computing"]),
        (None, "history", 1, ["History"]),
        ("Science Friday", "quantum", 1, ["Quantum Computing"]),
    ],
)
def test_load_summaries(
    podcast_filter, query, expected_count, expected_titles, mock_summaries
):
    paths = ["path1", "path2", "path3"]
    json_data = [json.dumps(summary) for summary in mock_summaries]

    m_open = mock_open()
    m_open.return_value.__enter__.return_value.read.side_effect = json_data

    with patch("builtins.open", m_open):
        with patch("json.load", side_effect=[json.loads(data) for data in json_data]):
            summaries = utils.load_summaries(
                paths, query=query, podcast_filter=podcast_filter
            )
            assert len(summaries) == expected_count
            titles = [summary["metadata"]["title"] for summary in summaries]
            assert titles == expected_titles


@pytest.mark.parametrize(
    "summary_id, expected_summary",
    [
        ("001", {"metadata": {"podcast": "Science Friday", "title": "Astrophysics"}}),
        ("002", {"metadata": {"podcast": "History Extra", "title": "History"}}),
    ],
)
def test_load_summary_by_id(summary_id, expected_summary):
    directory_path = "some_directory"
    expected_file_path = f"{directory_path}/{summary_id}.json"

    # Prepare mock data and setup mock_open
    json_data = json.dumps(expected_summary)
    m_open = mock_open(read_data=json_data)

    with patch("builtins.open", m_open) as mock_file:
        with patch("json.load", return_value=expected_summary):
            summary = utils.load_summary_by_id(directory_path, summary_id)
            mock_file.assert_called_once_with(expected_file_path, "r")
            assert summary == expected_summary
