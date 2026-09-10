# DailyBreadPlusNine

DailyBreadPlusNine creates a daily comparative reflection using four deliberately separated layers:

1. **Observed Sky** — verifiable astronomical facts, with NASA/JPL Horizons as the intended primary ephemeris source.
2. **Astrological Lens** — historically rooted symbolic interpretation, clearly labeled as interpretive rather than scientific.
3. **Human Theme** — an editorial bridge derived transparently from the astrological layer.
4. **The Plus Nine** — nine citations from religious or philosophical traditions that resonate with the theme without claiming doctrinal equivalence.

The core editorial rule is simple: astronomy supplies observations; astrology supplies symbolic interpretation; sacred texts are selected independently for thematic comparison.

## Getting started

Python 3.10 or newer is required.

```bash
python -m dailybread
```

Generate a specific date:

```bash
python -m dailybread --date 2026-09-10
```

Structured output:

```bash
python -m dailybread --date 2026-09-10 --format json
```

## Current architecture

- `dailybread/sky.py` — observed-sky provenance and NASA/JPL adapter boundary
- `dailybread/astrology.py` — symbolic interpretation layer
- `dailybread/theme_engine.py` — transparent theme derivation
- `dailybread/traditions.py` — curated comparative citation corpus
- `dailybread/generator.py` — composition and rendering
- `dailybread/model.py` — evidence-aware shared models

## Evidence classes

Every major content item is intended to remain identifiable as one of:

- `observed` — astronomical or ephemeris fact
- `interpretive` — astrological or symbolic reading
- `comparative` — thematic sacred-text comparison

This project does not treat astrology as scientific causation and does not claim that different religions teach identical doctrines.

## Important implementation status

The architecture has been rebuilt around the intended concept, but the live NASA/JPL Horizons request adapter is still pending. Until that adapter is implemented, `sky.py` returns a provenance-marked placeholder rather than inventing planetary positions. Sacred-text references in the starter corpus also require source-by-source editorial verification before public publication.

## Development

Run the automated tests:

```bash
python -m unittest discover -s tests -v
```
