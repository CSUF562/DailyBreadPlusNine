# DailyBreadPlusNine Architecture

## Purpose

DailyBreadPlusNine creates one daily reflection by connecting four clearly separated layers:

1. **Observed Sky** — verifiable astronomical observations and ephemeris data, preferably from NASA/JPL or similarly authoritative scientific sources.
2. **Astrological Lens** — traditional symbolic interpretation of the day's planetary and lunar configuration. This is explicitly interpretive, not presented as scientific causation.
3. **Human Theme** — a concise theme derived from the astrological lens, such as courage, restraint, generosity, grief, renewal, discernment, or stewardship.
4. **Plus Nine** — nine thematically resonant citations drawn from distinct religious or philosophical traditions, each preserved in its own context.

The synthesis must never claim that astronomy proves astrology or that different religions teach an identical doctrine. The system identifies thematic resonance, not equivalence.

## Evidence classes

Every generated claim should carry one of these internal evidence classes:

- `observed`: astronomical or calendar fact that can be sourced directly.
- `historical`: documented traditional association or historical astrological doctrine.
- `interpretive`: symbolic reading produced from the astrological layer.
- `comparative`: a cross-tradition thematic connection.

## Processing flow

```text
Date + location/time standard
        |
        v
Observed Sky adapter (NASA/JPL)
        |
        v
Astrological interpretation
        |
        v
Theme engine
        |
        v
Tradition corpus search / ranking
        |
        v
Nine citations + context notes
        |
        v
Daily synthesis + reflection
```

## Source policy

### Astronomy

Preferred sources include NASA/JPL resources, especially JPL ephemeris products or other authoritative NASA observational material. The program must retain source name, retrieval timestamp, and source URL/reference whenever live data is used.

### Astrology

Astrological meanings should be stored separately from astronomical data and attributed to a documented tradition or interpretive rule set. Astrology is presented as a symbolic framework.

### Religious and philosophical texts

Each citation record should include:

- tradition
- work / scripture
- citation or section reference
- short public-domain excerpt when permitted, otherwise reference + paraphrase
- theme tags
- context note
- source / edition metadata

The engine should prefer nine distinct traditions when the evidence base supports that. It should not force a weak match simply to reach nine.

## Proposed Python modules

- `dailybread/sky.py` — astronomical observation adapters and provenance.
- `dailybread/astrology.py` — symbolic interpretation rules.
- `dailybread/theme_engine.py` — converts interpreted factors into ranked human themes.
- `dailybread/traditions.py` — citation corpus, filtering, and resonance scoring.
- `dailybread/generator.py` — orchestration and output formatting.

## Daily publication

A GitHub Actions workflow should eventually run once per day, fetch or calculate the day's sky data, generate the entry, run validation tests, and publish/store the result. Scheduled publication should only be enabled once live source validation and citation-quality tests are in place.

## Non-negotiable editorial rules

1. Do not write or imply that NASA validates astrological claims.
2. Do not collapse religions into a single doctrine.
3. Distinguish observation from interpretation in the rendered output.
4. Preserve citation provenance.
5. Prefer an honest omission to a fabricated or weakly matched ninth citation.
