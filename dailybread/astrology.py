"""Astrological interpretation layer.

Astrology is treated as a symbolic/historical interpretive system, not as a
scientific claim. Inputs come from the observed-sky layer so provenance remains
explicit and science is never presented as validating astrological symbolism.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Dict, Iterable, List, Tuple

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

SIGNS: List[Tuple[str, str]] = [
    ("Aries", "initiative, courage, immediacy"),
    ("Taurus", "stability, value, embodiment"),
    ("Gemini", "exchange, curiosity, multiplicity"),
    ("Cancer", "care, belonging, memory"),
    ("Leo", "expression, vitality, visibility"),
    ("Virgo", "discernment, service, refinement"),
    ("Libra", "relationship, balance, reciprocity"),
    ("Scorpio", "depth, transformation, intensity"),
    ("Sagittarius", "meaning, expansion, belief"),
    ("Capricorn", "structure, responsibility, endurance"),
    ("Aquarius", "systems, community, innovation"),
    ("Pisces", "imagination, compassion, permeability"),
]

ASPECTS = [
    ("conjunction", 0.0, 8.0, "fusion, concentration, emphasis"),
    ("sextile", 60.0, 5.0, "opportunity, cooperation, exchange"),
    ("square", 90.0, 7.0, "friction, pressure, action"),
    ("trine", 120.0, 7.0, "flow, ease, reinforcement"),
    ("opposition", 180.0, 8.0, "polarity, encounter, balancing"),
]

PLANET_MEANINGS: Dict[str, str] = {
    "Sun": "identity, vitality, visibility, purpose",
    "Moon": "emotion, memory, receptivity, habit",
    "Mercury": "communication, learning, exchange, discernment",
    "Venus": "relationship, harmony, beauty, value",
    "Mars": "action, courage, conflict, protection",
    "Jupiter": "expansion, wisdom, law, generosity",
    "Saturn": "discipline, limits, duty, endurance",
    "Uranus": "disruption, freedom, innovation, awakening",
    "Neptune": "imagination, ideals, dissolution, compassion",
    "Pluto": "power, transformation, depth, renewal",
}

_LONGITUDE_RE = re.compile(r"^(\w+) apparent geocentric ecliptic longitude$")
_SEPARATION_RE = re.compile(r"^(\w+)-(\w+) geocentric angular separation$")
_NUMBER_RE = re.compile(r"(-?\d+(?:\.\d+)?)")


def _number(value: str) -> float | None:
    match = _NUMBER_RE.search(value)
    return float(match.group(1)) if match else None


def _sign_for(longitude: float) -> Tuple[str, float, str]:
    normalized = longitude % 360.0
    index = int(normalized // 30.0)
    sign, keywords = SIGNS[index]
    return sign, normalized % 30.0, keywords


def _aspect_for(separation: float):
    for name, exact, orb, keywords in ASPECTS:
        delta = abs(separation - exact)
        if delta <= orb:
            return name, exact, delta, keywords
    return None


def interpret(target_date: date, observations: Iterable[SkyObservation]) -> List[AstrologicalFactor]:
    """Interpret verified sky geometry through a clearly labeled astrology lens."""

    observations = list(observations)
    ruler, meanings = WEEKDAY_RULERS[target_date.weekday()]
    factors: List[AstrologicalFactor] = [
        AstrologicalFactor(
            label=f"Planetary weekday ruler: {ruler}",
            interpretation=meanings,
            tradition="Hellenistic/medieval planetary weekday tradition",
        )
    ]

    longitudes: Dict[str, float] = {}
    separations: List[Tuple[str, str, float]] = []

    for observation in observations:
        long_match = _LONGITUDE_RE.match(observation.label)
        if long_match:
            value = _number(observation.value)
            if value is not None:
                longitudes[long_match.group(1)] = value % 360.0
            continue

        separation_match = _SEPARATION_RE.match(observation.label)
        if separation_match:
            value = _number(observation.value)
            if value is not None:
                separations.append((separation_match.group(1), separation_match.group(2), value))

    for planet, longitude in longitudes.items():
        sign, degree, sign_keywords = _sign_for(longitude)
        planet_keywords = PLANET_MEANINGS.get(planet, "symbolic emphasis")
        factors.append(
            AstrologicalFactor(
                label=f"{planet} in {sign} at {degree:.2f}°",
                interpretation=f"{planet_keywords}; expressed through {sign_keywords}",
                tradition="Tropical zodiac interpretation of verified geocentric ecliptic longitude",
            )
        )

    for first, second, separation in separations:
        aspect = _aspect_for(separation)
        if not aspect:
            continue
        name, exact, delta, keywords = aspect
        factors.append(
            AstrologicalFactor(
                label=f"{first}-{second} {name} (orb {delta:.2f}°)",
                interpretation=(
                    f"{keywords}; interpreted between {PLANET_MEANINGS.get(first, first)} "
                    f"and {PLANET_MEANINGS.get(second, second)}"
                ),
                tradition="Major Ptolemaic aspect interpretation of verified angular separation",
            )
        )

    if len(factors) == 1:
        factors.append(
            AstrologicalFactor(
                label="Live sky interpretation unavailable",
                interpretation="Only the planetary weekday ruler could be interpreted because verified longitudes were unavailable.",
                tradition="DailyBreadPlusNine evidence rule",
            )
        )

    return factors
