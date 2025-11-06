# DailyBreadPlusNine

DailyBreadPlusNine generates a daily reflection that fuses NASA-inspired science notes with mindful prompts and gratitude sparks. The "plus nine" comes from the nine invitations delivered each day—three reflections, three mindful actions, and three gratitude sparks.

## Getting started

This project uses the Python standard library only. You can run the generator directly with the module entrypoint:

```bash
python -m dailybread
```

To produce the insight for a specific date, supply the `--date` flag (format `YYYY-MM-DD`). Use `--format json` if you prefer structured output.

```bash
python -m dailybread --date 2025-02-25 --format json
```

## Development

Run the automated tests with `pytest`:

```bash
pytest
```
