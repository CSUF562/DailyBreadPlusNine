"""Comparative sacred-text layer for DailyBreadPlusNine.

This module stores thematic references, not claims of doctrinal equivalence.
Each citation should be reviewed for context, translation, and tradition-specific
meaning before publication.
"""

from __future__ import annotations

from typing import Dict, List

from .model import TraditionCitation


# Starter corpus. These are citation references and context notes only. Full
# copyrighted translations are intentionally not embedded here.
CITATIONS: List[TraditionCitation] = [
    TraditionCitation(
        tradition="Christianity",
        work="New Testament",
        citation="Matthew 25:14-30",
        theme_tags=["stewardship", "responsibility", "gifts", "action"],
        context_note="Parable of entrusted talents; often read through stewardship, accountability, and faithful action.",
    ),
    TraditionCitation(
        tradition="Judaism",
        work="Proverbs",
        citation="Proverbs 11:24-25",
        theme_tags=["generosity", "abundance", "service", "reciprocity"],
        context_note="Wisdom teaching connecting generosity with flourishing; should be read within the larger ethical tradition of Proverbs.",
    ),
    TraditionCitation(
        tradition="Islam",
        work="Qur'an",
        citation="2:261",
        theme_tags=["generosity", "charity", "abundance", "service"],
        context_note="Uses an agricultural image to describe multiplied benefit from giving in the way of God.",
    ),
    TraditionCitation(
        tradition="Hindu traditions",
        work="Bhagavad Gita",
        citation="3.19",
        theme_tags=["action", "duty", "detachment", "service"],
        context_note="Situated within Krishna's teaching on disciplined action without attachment to personal reward.",
    ),
    TraditionCitation(
        tradition="Buddhism",
        work="Dhammapada",
        citation="Verse 183",
        theme_tags=["discipline", "ethical action", "mind", "restraint"],
        context_note="Compact summary of avoiding harm, cultivating good, and purifying the mind within Buddhist ethical practice.",
    ),
    TraditionCitation(
        tradition="Sikhism",
        work="Guru Granth Sahib",
        citation="Ang 1245",
        theme_tags=["service", "humility", "truth", "action"],
        context_note="Representative Sikh emphasis on truthful living and service; exact translation should be verified for publication.",
    ),
    TraditionCitation(
        tradition="Taoism",
        work="Tao Te Ching",
        citation="Chapter 81",
        theme_tags=["giving", "service", "simplicity", "wisdom"],
        context_note="Traditionally associated with non-hoarding wisdom, giving, and benefiting others without depletion.",
    ),
    TraditionCitation(
        tradition="Jainism",
        work="Tattvartha Sutra",
        citation="5.21",
        theme_tags=["interdependence", "service", "responsibility", "life"],
        context_note="Associated with the Jain principle of mutual support and interdependence among living beings.",
    ),
    TraditionCitation(
        tradition="Baha'i Faith",
        work="Hidden Words",
        citation="Persian 80",
        theme_tags=["service", "humanity", "generosity", "purpose"],
        context_note="Baha'i writings strongly emphasize service to humanity; exact wording should be sourced from an authorized edition.",
    ),
]


def find_by_theme(theme: str, limit: int = 9) -> List[TraditionCitation]:
    """Return up to *limit* citations ranked by simple thematic overlap."""

    words = {part.strip().lower() for part in theme.replace("/", " ").replace(",", " ").split() if part.strip()}
    ranked = sorted(
        CITATIONS,
        key=lambda item: sum(1 for tag in item.theme_tags if tag.lower() in words),
        reverse=True,
    )
    return ranked[:limit]
