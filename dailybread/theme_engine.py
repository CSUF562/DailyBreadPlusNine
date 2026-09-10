"""Theme derivation for DailyBreadPlusNine.

Themes are editorial bridges. They are not scientific conclusions and should
always be traceable back to clearly labeled astrological factors.
"""

from __future__ import annotations

from collections import Counter
from typing import Iterable

from .model import AstrologicalFactor, ThemeCandidate


THEME_MAP = {
    "Moon": ["care", "memory", "receptivity"],
    "Mars": ["courage", "right action", "restraint"],
    "Mercury": ["discernment", "communication", "learning"],
    "Jupiter": ["wisdom", "generosity", "stewardship"],
    "Venus": ["relationship", "harmony", "value"],
    "Saturn": ["discipline", "responsibility", "endurance"],
    "Sun": ["purpose", "integrity", "vitality"],
}


def derive_theme(factors: Iterable[AstrologicalFactor]) -> ThemeCandidate:
    """Derive one transparent editorial theme from symbolic factors."""

    counter: Counter[str] = Counter()
    reasons = []
    for factor in factors:
        reasons.append(f"{factor.label}: {factor.interpretation}")
        for ruler, themes in THEME_MAP.items():
            if ruler.lower() in factor.label.lower():
                counter.update(themes)

    if not counter:
        return ThemeCandidate(
            theme="discernment",
            score=0.25,
            rationale="Fallback editorial theme used because no mapped astrological factor was available.",
        )

    selected, count = counter.most_common(1)[0]
    return ThemeCandidate(
        theme=selected,
        score=min(1.0, 0.5 + (0.1 * count)),
        rationale="; ".join(reasons),
    )
