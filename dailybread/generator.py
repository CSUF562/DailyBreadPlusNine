"""Core logic for DailyBreadPlusNine."""

from __future__ import annotations

import functools
import hashlib
import json
import random
from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Sequence

from importlib import resources


@dataclass(frozen=True)
class DailyBreadEntry:
    """Represents a single day of Daily Bread content."""

    target_date: date
    cosmic_focus: Dict[str, str]
    meaning_thread: Dict[str, str]
    reflection_prompts: List[str]
    mindful_actions: List[str]
    gratitude_prompts: List[str]
    affirmation: str

    def to_dict(self) -> Dict[str, object]:
        """Return a JSON-friendly representation of the entry."""

        return {
            "date": self.target_date.isoformat(),
            "cosmic_focus": self.cosmic_focus,
            "meaning_thread": self.meaning_thread,
            "reflection_prompts": self.reflection_prompts,
            "mindful_actions": self.mindful_actions,
            "gratitude_prompts": self.gratitude_prompts,
            "affirmation": self.affirmation,
        }

    def to_text(self) -> str:
        """Render the entry as formatted text."""

        lines: List[str] = []
        lines.append(f"Daily Bread for {self.target_date:%A, %B %d, %Y}")
        lines.append("")
        lines.append(f"Cosmic Focus — {self.cosmic_focus['title']}")
        lines.append(f"  {self.cosmic_focus['summary']}")
        lines.append(f"  Connection: {self.cosmic_focus['connection']}")
        lines.append("")
        lines.append(f"Meaning Thread — {self.meaning_thread['theme']}")
        lines.append(f"  {self.meaning_thread['invitation']}")
        lines.append("")
        lines.append("Reflection Prompts:")
        for idx, prompt in enumerate(self.reflection_prompts, 1):
            lines.append(f"  {idx}. {prompt}")
        lines.append("")
        lines.append("Mindful Actions:")
        for idx, action in enumerate(self.mindful_actions, 1):
            lines.append(f"  {idx}. {action}")
        lines.append("")
        lines.append("Gratitude Sparks:")
        for idx, spark in enumerate(self.gratitude_prompts, 1):
            lines.append(f"  {idx}. {spark}")
        lines.append("")
        lines.append(f"Affirmation: {self.affirmation}")
        return "\n".join(lines)


def generate_entry(target_date: date | None = None) -> DailyBreadEntry:
    """Generate a Daily Bread entry for a specific date."""

    target_date = target_date or date.today()
    cosmic_focus = _select_single("nasa_insights", target_date, "cosmic")
    meaning_thread = _select_single("meaning_threads", target_date, "meaning")
    reflections = _select_multiple("reflection_prompts", 3, target_date, "reflect")
    practices = _select_multiple("micro_practices", 3, target_date, "practice")
    gratitudes = _select_multiple("gratitude_prompts", 3, target_date, "gratitude")
    affirmation = _select_single("affirmations", target_date, "affirmation")
    return DailyBreadEntry(
        target_date=target_date,
        cosmic_focus=cosmic_focus,
        meaning_thread=meaning_thread,
        reflection_prompts=reflections,
        mindful_actions=practices,
        gratitude_prompts=gratitudes,
        affirmation=affirmation,
    )


def _dataset_path(name: str) -> resources.abc.Traversable:
    return resources.files(__package__).joinpath("data").joinpath(f"{name}.json")


@functools.lru_cache(maxsize=None)
def _load_dataset(name: str):
    with _dataset_path(name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _select_single(dataset_name: str, target_date: date, label: str):
    dataset = _load_dataset(dataset_name)
    index = _deterministic_index(len(dataset), target_date, label)
    return dataset[index]


def _select_multiple(dataset_name: str, count: int, target_date: date, label: str) -> List[str]:
    dataset: Sequence[str] = _load_dataset(dataset_name)
    rng = random.Random(_seed_for(target_date, label))
    if count >= len(dataset):
        ordered = list(dataset)
        ordered.sort()
        return ordered
    return rng.sample(list(dataset), count)


def _deterministic_index(length: int, target_date: date, label: str) -> int:
    if length == 0:
        raise ValueError(f"Dataset '{label}' is empty")
    seed = _seed_for(target_date, label)
    return seed % length


def _seed_for(target_date: date, label: str) -> int:
    digest = hashlib.sha256(f"{target_date.isoformat()}::{label}".encode("utf-8")).hexdigest()
    return int(digest, 16)
