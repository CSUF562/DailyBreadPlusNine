"""Astrological interpretation layer.

Astrology is treated as a symbolic/historical interpretive system, not as a
scientific claim. Inputs should come from the observed-sky layer so provenance
remains explicit.
"""

from __future__ import annotations

from datetime import date
from typing import Iterable, List

from .model import AstrologicalFactor, SkyObservation


WEEKDAY_RULERS = {
    0: ("Moon", "receptivity, memory, care, habit"),
    1: ("Mars", "action, courage, conflict, protection"),
    2: ("Mercury", "communication, learning, exchange, discernment"),
    3: ("Jupiter", "expansion, wisdom, law, generosity"),
    4: ("Venus", "relationship, harmony, beauty, value"),
    5: ("Saturn", "discipline, limits, duty, endurance"),
    6: ("Sun", "identity, vitality, visibility, purpose"),
}


def interpret(target_date: date, observations: Iterable[SkyObservation]) -> List[AstrologicalFactor]:
    """Return clearly labeled symbolic factors for a date and sky state."""

    ruler, meanings = WEEKDAY_RULERS[target_date.weekday()]
    factors = [
        AstrologicalFactor(
            label=f"Planetary weekday ruler: {ruler}",
            interpretation=meanings,
            tradition="Hellenistic/medieval planetary weekday tradition",
        )
    ]

    # Future passes will add factors from actual Sun/Moon/planetary positions
    # and aspects supplied by the observed-sky layer.
    if list(observations):
        factors.append(
            AstrologicalFactor(
                label="Observed sky available",
                interpretation="Use verified ephemeris facts as the physical context before adding symbolic meaning.",
                tradition="DailyBreadPlusNine evidence rule",
            )
        )
    return factors
