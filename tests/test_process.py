from unittest.mock import patch

import pytest

from src.process import list_files


def test_list_files_with_various_files():
    """Test listing files with expected and unexpected file types."""
    with patch("os.listdir") as mock_listdir, patch("os.path.isdir") as mock_isdir:
        mock_isdir.return_value = True
        # Include a variety of file types and names
        mock_listdir.return_value = [
            "example.txt",
            "report.pdf",
            "image.png",
            "notes.txt",
            "diagram.svg",
        ]
        # Expect only txt files
        expected = ["/fakepath/example.txt", "/fakepath/notes.txt"]
        assert list_files("/fakepath", "txt") == expected


def test_list_files_no_files():
    """Test directory with no matching file types and empty directory."""
    with patch("os.listdir") as mock_listdir, patch("os.path.isdir") as mock_isdir:
        mock_isdir.return_value = True
        # No txt files
        mock_listdir.return_value = ["data.pdf", "image.png"]
        assert list_files("/fakepath", "txt") == []
        # Empty directory
        mock_listdir.return_value = []
        assert list_files("/fakepath", "txt") == []


def test_invalid_directory():
    """Test behavior with an invalid directory path."""
    with patch("os.path.isdir") as mock_isdir:
        mock_isdir.return_value = False
        with pytest.raises(ValueError):
            list_files("/invalidpath", "txt")
