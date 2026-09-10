"""Transparent dual relevance scoring for comparative citations."""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable, List

from .model import AstrologicalFactor, RelevanceScore, SkyObservation, TraditionCitation


def _tokens(text: str) -> set[str]:
    cleaned = text.lower().replace("/", " ").replace(",", " ").replace("—", " ").replace("-", " ")
    return {part.strip(" .:;()[]") for part in cleaned.split() if part.strip(" .:;()[]")}


def score_citation(
    citation: TraditionCitation,
    observations: Iterable[SkyObservation],
    astrological_factors: Iterable[AstrologicalFactor],
) -> TraditionCitation:
    tags = {tag.lower() for tag in citation.theme_tags}
    observation_words = set()
    for observation in observations:
        observation_words |= _tokens(f"{observation.label} {observation.value}")
    astrology_words = set()
    for factor in astrological_factors:
        astrology_words |= _tokens(f"{factor.label} {factor.interpretation}")

    astro_hits = sorted(tags & observation_words)
    symbolic_hits = sorted(tags & astrology_words)

    # Scores are intentionally conservative until live ephemeris facts exist.
    # A citation cannot earn a strong astronomical score from symbolic keywords alone.
    astronomical = min(100, len(astro_hits) * 25)
    astrological = min(100, len(symbolic_hits) * 20)

    astronomical_reason = (
        "Direct thematic overlap with observed-sky descriptors: " + ", ".join(astro_hits)
        if astro_hits
        else "No direct thematic overlap with the current observed-sky descriptors."
    )
    astrological_reason = (
        "Thematic overlap with the symbolic astrological lens: " + ", ".join(symbolic_hits)
        if symbolic_hits
        else "No direct thematic overlap with the current astrological descriptors."
    )

    return replace(
        citation,
        relevance=RelevanceScore(
            astronomical=astronomical,
            astrological=astrological,
            astronomical_reason=astronomical_reason,
            astrological_reason=astrological_reason,
        ),
    )


def rank_citations(
    citations: Iterable[TraditionCitation],
    observations: Iterable[SkyObservation],
    astrological_factors: Iterable[AstrologicalFactor],
    basis: str = "balanced",
) -> List[TraditionCitation]:
    if basis not in {"astronomy", "astrology", "balanced"}:
        raise ValueError("basis must be astronomy, astrology, or balanced")
    scored = [score_citation(item, observations, astrological_factors) for item in citations]
    return sorted(
        scored,
        key=lambda item: item.relevance.score_for(basis) if item.relevance else 0,
        reverse=True,
    )
