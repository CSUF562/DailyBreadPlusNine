from datetime import date

from dailybread.generator import DailyBreadEntry, generate_entry


def test_generate_entry_is_deterministic():
    target = date(2025, 2, 25)
    first = generate_entry(target)
    second = generate_entry(target)
    assert first == second


def test_entry_structure():
    entry = generate_entry(date(2024, 12, 9))
    assert isinstance(entry, DailyBreadEntry)
    assert set(entry.cosmic_focus) == {"title", "summary", "connection"}
    assert len(entry.reflection_prompts) == 3
    assert len(entry.mindful_actions) == 3
    assert len(entry.gratitude_prompts) == 3
    assert isinstance(entry.affirmation, str)
