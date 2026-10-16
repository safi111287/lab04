import pytest

from tvsummary import Show


@pytest.fixture
def sample_shows() -> list[Show]:
    """Provide handmade shows for aggregation tests."""
    return [
        Show(
            {
                "name": "First Show",
                "language": "English",
                "genres": ["Drama", "Comedy"],
                "rating": {"average": 8.0},
                "network": {"name": "ABC"},
                "premiered": "2015-04-10",
            }
        ),
        Show(
            {
                "name": "Second Show",
                "language": "English",
                "genres": ["Drama"],
                "rating": {"average": 6.0},
                "network": {"name": "ABC"},
                "premiered": "2018-06-20",
            }
        ),
        Show(
            {
                "name": "Third Show",
                "language": "Japanese",
                "genres": None,
                "rating": {"average": None},
                "network": None,
                "premiered": None,
            }
        ),
    ]
