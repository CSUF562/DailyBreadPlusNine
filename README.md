# DailyBreadPlusNine

DailyBreadPlusNine generates a daily reflection that fuses NASA-inspired science notes with mindful prompts and gratitude sparks. The "plus nine" comes from the nine invitations delivered each day—three reflections, three mindful actions, and three gratitude sparks.

## Getting started

This project requires Python 3.10 or newer and uses the Python standard library only. From the repository root, run the generator directly with the module entrypoint:

```bash
python -m dailybread
```

To produce the insight for a specific date, supply the `--date` flag (format `YYYY-MM-DD`). Use `--format json` if you prefer structured output.

```bash
python -m dailybread --date 2025-02-25 --format json
```

Dates must be valid calendar dates written exactly as `YYYY-MM-DD`. Results are deterministic: the same date always produces the same insight and nine prompts. The science highlights are curated, NASA-inspired examples stored in this repository; they are not live NASA data.

## Development

Run the automated tests without installing any additional dependencies:

```bash
python -m unittest discover -s tests -v
```
