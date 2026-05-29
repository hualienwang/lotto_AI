import random
from datetime import datetime

import re

def parse_numbers(numbers_text):
    """
    Parse a string of numbers into a list of integers.
    Supports comma-separated, space-separated, and mixed separators.
    """
    numbers = []
    for value in re.split(r'[\s,，]+', str(numbers_text).strip()):
        if not value:
            continue
        try:
            number = int(value.strip())
        except ValueError:
            continue
        if 1 <= number <= 39 and number not in numbers:
            numbers.append(number)
    return numbers

def normalize_scores(raw_scores):
    """
    Normalize raw scores to a 0-1 range.
    """
    if not raw_scores:
        return {}
    values = list(raw_scores.values())
    min_value = min(values)
    max_value = max(values)
    if max_value == min_value:
        return {number: 0.5 for number in raw_scores}
    return {
        number: (value - min_value) / (max_value - min_value)
        for number, value in raw_scores.items()
    }

def weighted_pick(scores, count=5):
    """
    Pick numbers based on weighted scores.
    """
    available = list(scores.keys())
    picked = []
    while available and len(picked) < count:
        # Add a small base weight (0.05) to ensure all numbers have a chance.
        weights = [max(scores[number], 0) + 0.05 for number in available]
        selected = random.choices(available, weights=weights, k=1)[0]
        picked.append(selected)
        available.remove(selected)
    return sorted(picked)

def next_period_from_draws(draws):
    """
    Determine the next period number based on the most recent draw.
    """
    if not draws:
        return '1'
    try:
        return str(int(draws[0]['period']) + 1)
    except (ValueError, KeyError, TypeError):
        return datetime.now().strftime('%Y%m%d%H%M')
