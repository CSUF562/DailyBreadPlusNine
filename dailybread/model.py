"""Shared evidence-aware data models for DailyBreadPlusNine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional


@dataclass(frozen=True)
class SourceRef:
    name: str
    reference: str
    url: Optional[str] = None
    retrieved_at: Optional[datetime] = None


@dataclass(frozen=True)
class SkyObservation:
    label: str
    value: str
    source: SourceRef
    evidence_class: str = "observed"


@dataclass(frozen=True)
class AstrologicalFactor:
    label: str
    interpretation: str
    tradition: str
    source: Optional[SourceRef] = None
    evidence_class: str = "interpretive"


@dataclass(frozen=True)
class ThemeCandidate:
    theme: str
    score: float
    rationale: str


@dataclass(frozen=True)
class RelevanceScore:
    """Transparent relevance scores for one comparative citation.

    Scores describe editorial/thematic fit only. They do not measure scientific
    truth, causation, or doctrinal equivalence.
    """

    astronomical: int
    astrological: int
    astronomical_reason: str
    astrological_reason: str

    def score_for(self, basis: str) -> float:
        if basis == "astronomy":
            return float(self.astronomical)
        if basis == "astrology":
            return float(self.astrological)
        return (self.astronomical + self.astrological) / 2.0


@dataclass(frozen=True)
class TraditionCitation:
    tradition: str
    work: str
    citation: str
    theme_tags: List[str]
    context_note: str
    excerpt: Optional[str] = None
    source: Optional[SourceRef] = None
    relevance: Optional[RelevanceScore] = None
    evidence_class: str = "comparative"


@dataclass(frozen=True)
class DailyComparativeEntry:
    target_date: date
    observations: List[SkyObservation] = field(default_factory=list)
    astrological_factors: List[AstrologicalFactor] = field(default_factory=list)
    primary_theme: Optional[ThemeCandidate] = None
    citations: List[TraditionCitation] = field(default_factory=list)
    ranking_basis: str = "balanced"
    synthesis: str = ""
    reflection: str = ""
