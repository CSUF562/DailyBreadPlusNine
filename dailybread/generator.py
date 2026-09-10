"""Core DailyBreadPlusNine pipeline.

Observed sky facts, astrological interpretation, theme selection, and sacred-text
comparisons are kept as distinct stages so their evidence status is never blurred.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import date
from typing import Dict, List

from .astrology import interpret
from .model import DailyComparativeEntry
from .relevance import rank_citations
from .sky import observations_for
from .theme_engine import derive_theme
from .traditions import find_by_theme


class DailyBreadEntry(DailyComparativeEntry):
    """Renderable daily comparative entry."""

    def to_dict(self) -> Dict[str, object]:
        payload = asdict(self)
        payload["target_date"] = self.target_date.isoformat()
        return payload

    def to_text(self) -> str:
        lines: List[str] = []
        lines.append(f"Daily Bread + Nine for {self.target_date:%A, %B %d, %Y}")
        lines.append(f"Ranking basis: {self.ranking_basis}")
        lines.append("")
        lines.append("Observed Sky")
        for observation in self.observations:
            lines.append(f"  • {observation.label}: {observation.value}")
            lines.append(f"    Source: {observation.source.name} — {observation.source.reference}")
        lines.append("")
        lines.append("Astrological Lens")
        for factor in self.astrological_factors:
            lines.append(f"  • {factor.label}: {factor.interpretation}")
            lines.append(f"    Tradition: {factor.tradition}")
        lines.append("")
        if self.primary_theme:
            lines.append(f"Human Theme — {self.primary_theme.theme.title()}")
            lines.append(f"  {self.primary_theme.rationale}")
            lines.append("")
        lines.append("The Plus Nine")
        for idx, citation in enumerate(self.citations, 1):
            lines.append(f"  {idx}. {citation.tradition} — {citation.work}, {citation.citation}")
            if citation.relevance:
                lines.append(
                    f"     Relevance: astronomy {citation.relevance.astronomical}/100 | "
                    f"astrology {citation.relevance.astrological}/100"
                )
            lines.append(f"     {citation.context_note}")
        lines.append("")
        lines.append("Common Thread")
        lines.append(f"  {self.synthesis}")
        lines.append("")
        lines.append("Daily Reflection")
        lines.append(f"  {self.reflection}")
        return "\n".join(lines)


def generate_entry(target_date: date | None = None, ranking_basis: str = "balanced") -> DailyBreadEntry:
    """Generate a source-separated Daily Bread + Nine entry.

    ranking_basis may be ``astronomy``, ``astrology``, or ``balanced``.
    """

    target_date = target_date or date.today()
    observations = observations_for(target_date)
    astrological_factors = interpret(target_date, observations)
    theme = derive_theme(astrological_factors)
    candidate_citations = find_by_theme(theme.theme, limit=9)
    citations = rank_citations(
        candidate_citations,
        observations,
        astrological_factors,
        basis=ranking_basis,
    )

    synthesis = (
        f"These traditions are not being presented as doctrinally equivalent. "
        f"They are placed in conversation around the editorial theme of {theme.theme}. "
        f"The displayed order is currently ranked by {ranking_basis} relevance."
    )
    reflection = f"Where might {theme.theme} require more conscious practice in my life today?"

    return DailyBreadEntry(
        target_date=target_date,
        observations=observations,
        astrological_factors=astrological_factors,
        primary_theme=theme,
        citations=citations,
        ranking_basis=ranking_basis,
        synthesis=synthesis,
        reflection=reflection,
    )
