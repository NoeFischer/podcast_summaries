import pytest

from app import utils


# convert_date
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
