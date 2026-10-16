import random

from tvsummary.models import Show
from tvsummary.sampling import select_featured_shows


def test_same_seed_repeats_sample(sample_shows: list[Show]) -> None:
    first = select_featured_shows(sample_shows, seed=42, sample_size=2)
    second = select_featured_shows(sample_shows, seed=42, sample_size=2)

    assert first == second
    assert len(first) == 2
    assert len(set(first)) == 2
    assert set(first) <= {show.name for show in sample_shows}


def test_sample_larger_than_records(sample_shows: list[Show]) -> None:
    result = select_featured_shows(sample_shows, seed=42, sample_size=10)

    assert sorted(result) == sorted(show.name for show in sample_shows)


def test_empty_records() -> None:
    assert select_featured_shows([], seed=42, sample_size=5) == []


def test_zero_sample_size(sample_shows: list[Show]) -> None:
    assert select_featured_shows(sample_shows, seed=42, sample_size=0) == []


def test_sampling_preserves_input(sample_shows: list[Show]) -> None:
    original = sample_shows.copy()

    select_featured_shows(sample_shows, seed=42, sample_size=2)

    assert sample_shows == original


def test_sampling_preserves_global_random_state(
    sample_shows: list[Show],
) -> None:
    original_state = random.getstate()

    select_featured_shows(sample_shows, seed=42, sample_size=2)

    assert random.getstate() == original_state
