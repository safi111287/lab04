import random

from .models import Show


def select_featured_shows(
    records: list[Show], seed: int, sample_size: int
) -> list[str]:
    """Choose a repeatable sample without changing the records."""
    generator = random.Random(seed)
    count = min(sample_size, len(records))
    selected = generator.sample(records, count)
    return [show.name for show in selected]
