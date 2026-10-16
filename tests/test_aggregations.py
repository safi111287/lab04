from tvsummary import (
    AverageRatingByLanguage,
    DataQuirks,
    Show,
    ShowsPerDecade,
    ShowsPerGenre,
    ShowsPerNetwork,
)


def test_shows_per_genre(sample_shows: list[Show]) -> None:
    result = ShowsPerGenre().compute(sample_shows)
    assert result == {"Drama": 2, "Comedy": 1}


def test_average_rating_by_language(sample_shows: list[Show]) -> None:
    result = AverageRatingByLanguage().compute(sample_shows)
    assert result == {"English": 7.0}


def test_shows_per_network(sample_shows: list[Show]) -> None:
    result = ShowsPerNetwork().compute(sample_shows)
    assert result == {"ABC": 2, "No Network": 1}


def test_shows_per_decade(sample_shows: list[Show]) -> None:
    result = ShowsPerDecade().compute(sample_shows)
    assert result == {"2010s": 2}


def test_data_quirks(sample_shows: list[Show]) -> None:
    result = DataQuirks().compute(sample_shows)
    assert result == {
        "shows_without_genres": 1,
        "shows_without_rating": 1,
        "shows_without_network": 1,
        "shows_without_premiered_date": 1,
        "unique_languages": ["English", "Japanese"],
    }
