"""Comparative sacred-text layer for DailyBreadPlusNine.

This module stores thematic references, not claims of doctrinal equivalence.
Each citation should be reviewed for context, translation, and tradition-specific
meaning before publication.
"""

from __future__ import annotations

from typing import List

from .model import SourceRef, TraditionCitation


# Curated starter corpus. Excerpts are deliberately short; source metadata
# identifies the translation/edition that must be consulted for fuller context.
CITATIONS: List[TraditionCitation] = [
    TraditionCitation(
        tradition="Christianity",
        work="Gospel according to Matthew",
        citation="Matthew 25:14-30",
        theme_tags=["stewardship", "responsibility", "gifts", "action"],
        context_note="This parable of entrusted talents is commonly read in Christianity through stewardship, accountability, and faithful action.",
        translation="King James Version (KJV)",
        excerpt="Well done, thou good and faithful servant.",
        source=SourceRef(name="Bible Gateway", reference="Matthew 25:21, KJV", url="https://www.biblegateway.com/passage/?search=Matthew%2025%3A21&version=KJV"),
    ),
    TraditionCitation(
        tradition="Judaism",
        work="Book of Proverbs",
        citation="Proverbs 11:24-25",
        theme_tags=["generosity", "abundance", "service", "reciprocity"],
        context_note="This wisdom saying connects generosity with flourishing within Proverbs' broader Jewish ethical tradition.",
        translation="Jewish Publication Society (JPS 1917)",
        excerpt="The beneficent soul shall be made rich.",
        source=SourceRef(name="Sefaria", reference="Proverbs 11:25, JPS 1917", url="https://www.sefaria.org/Proverbs.11.25?lang=bi"),
    ),
    TraditionCitation(
        tradition="Islam",
        work="Qur'an",
        citation="2:261",
        theme_tags=["generosity", "charity", "abundance", "service"],
        context_note="The verse uses an agricultural image for multiplied benefit from giving in the way of God, not a general promise of material return.",
        translation="Marmaduke Pickthall, The Meaning of the Glorious Koran",
        excerpt="The likeness of those who spend their wealth in Allah's way is as the likeness of a grain.",
        source=SourceRef(name="Quran.com", reference="Al-Baqarah 2:261, Pickthall", url="https://quran.com/2/261?translations=19"),
    ),
    TraditionCitation(
        tradition="Hindu traditions",
        work="Bhagavad Gita",
        citation="3.19",
        theme_tags=["action", "duty", "detachment", "service"],
        context_note="Krishna's counsel occurs within the Gita's teaching on disciplined action and duty without attachment to personal reward.",
        translation="Annie Besant and Bhagavan Das (1905)",
        excerpt="Therefore, without attachment, constantly perform action which is duty.",
        source=SourceRef(name="Internet Sacred Text Archive", reference="Bhagavad Gita 3.19, Besant and Das", url="https://sacred-texts.com/hin/sbg/sbg14.htm"),
    ),
    TraditionCitation(
        tradition="Buddhism",
        work="Dhammapada",
        citation="Verse 183",
        theme_tags=["discipline", "ethical action", "mind", "restraint"],
        context_note="This verse is a compact summary of avoiding harm, cultivating good, and purifying the mind within Buddhist ethical practice.",
        translation="F. Max Muller, Sacred Books of the East, Vol. 10 (1881)",
        excerpt="Not to commit any sin, to do good, and to purify one's mind.",
        source=SourceRef(name="Internet Sacred Text Archive", reference="Dhammapada 183, Max Muller", url="https://sacred-texts.com/bud/sbe10/sbe10185.htm"),
    ),
    TraditionCitation(
        tradition="Sikhism",
        work="Sri Guru Granth Sahib",
        citation="Ang 62",
        theme_tags=["service", "humility", "truth", "action"],
        context_note="Guru Nanak's line distinguishes merely speaking about truth from embodying truthful conduct in Sikh life.",
        translation="Sant Singh Khalsa",
        excerpt="Truth is higher than everything; but higher still is truthful living.",
        source=SourceRef(name="SriGranth.org", reference="Sri Guru Granth Sahib, Ang 62", url="https://www.srigranth.org/servlet/gurbani.gurbani?Action=Page&Param=62&english=t"),
    ),
    TraditionCitation(
        tradition="Taoism",
        work="Tao Te Ching",
        citation="Chapter 81",
        theme_tags=["giving", "service", "simplicity", "wisdom"],
        context_note="In the chapter's Daoist frame, the sage benefits others without hoarding and is not diminished by giving.",
        translation="James Legge (1891)",
        excerpt="The sage does not accumulate for himself.",
        source=SourceRef(name="Chinese Text Project", reference="Dao De Jing 81, James Legge", url="https://ctext.org/dao-de-jing/ens"),
    ),
    TraditionCitation(
        tradition="Jainism",
        work="Tattvartha Sutra",
        citation="5.21",
        theme_tags=["interdependence", "service", "responsibility", "life"],
        context_note="This aphorism expresses mutual support among living beings within Jain teachings on souls, ethics, and interdependence.",
        translation="Nathmal Tatia (1994)",
        excerpt="The function of souls is to help one another.",
        source=SourceRef(name="Wisdomlib", reference="Tattvartha Sutra 5.21", url="https://www.wisdomlib.org/jainism/book/tattvartha-sutra-with-commentary/d/doc1084775.html"),
    ),
    TraditionCitation(
        tradition="Baha'i Faith",
        work="The Hidden Words",
        citation="Persian no. 80",
        theme_tags=["service", "humanity", "generosity", "purpose"],
        context_note="Baha'u'llah contrasts universally available words with deeds that demonstrate spiritual commitment in practice.",
        translation="Authorized English translation",
        excerpt="Guidance hath ever been given by words, and now it is given by deeds.",
        source=SourceRef(name="Baha'i Reference Library", reference="The Hidden Words, Persian no. 80", url="https://www.bahai.org/library/authoritative-texts/bahaullah/hidden-words/3#623891128"),
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
