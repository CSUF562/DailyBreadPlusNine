"""Observed-sky layer backed by NASA/JPL Horizons.

This module contains only astronomical/ephemeris facts. Astrological signs,
aspects, rulerships, and symbolic meanings belong in ``astrology.py``.
"""

from __future__ import annotations

import csv
import io
import json
import math
from datetime import date, datetime, timedelta, timezone
from functools import lru_cache
from typing import Dict, List
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .model import SkyObservation, SourceRef


HORIZONS_API = "https://ssd.jpl.nasa.gov/api/horizons.api"
CENTER = "500@399"  # Earth geocenter

JPL_HORIZONS = SourceRef(
    name="NASA/JPL Horizons",
    reference="Solar System Dynamics ephemeris service",
    url="https://ssd.jpl.nasa.gov/horizons/",
)

BODIES: Dict[str, str] = {
    "Sun": "10",
    "Moon": "301",
    "Mercury": "199",
    "Venus": "299",
    "Mars": "499",
    "Jupiter": "599",
    "Saturn": "699",
    "Uranus": "799",
    "Neptune": "899",
    "Pluto": "999",
}


def _quoted(value: str) -> str:
    return f"'{value}'"


def _request_url(body_id: str, target_date: date, quantities: str) -> str:
    """Build a Horizons observer-table request for 12:00 UTC on target_date."""

    start = datetime.combine(target_date, datetime.min.time(), tzinfo=timezone.utc).replace(hour=12)
    stop = start + timedelta(minutes=1)
    params = {
        "format": "json",
        "COMMAND": _quoted(body_id),
        "EPHEM_TYPE": _quoted("OBSERVER"),
        "CENTER": _quoted(CENTER),
        "START_TIME": _quoted(start.strftime("%Y-%m-%d %H:%M")),
        "STOP_TIME": _quoted(stop.strftime("%Y-%m-%d %H:%M")),
        "STEP_SIZE": _quoted("1 m"),
        "QUANTITIES": _quoted(quantities),
        "CSV_FORMAT": _quoted("YES"),
        "OBJ_DATA": _quoted("NO"),
        "ANG_FORMAT": _quoted("DEG"),
    }
    return f"{HORIZONS_API}?{urlencode(params)}"


@lru_cache(maxsize=512)
def _fetch_horizons_row(body_id: str, iso_date: str, quantities: str) -> Dict[str, str]:
    """Fetch and parse the first CSV observer-table row from Horizons.

    The in-process cache prevents duplicate requests during one generation run.
    Horizons embeds ``$$SOE`` and ``$$EOE`` markers specifically to support
    machine parsing of ephemeris tables.
    """

    target_date = date.fromisoformat(iso_date)
    request = Request(
        _request_url(body_id, target_date, quantities),
        headers={"User-Agent": "DailyBreadPlusNine/0.2 (+GitHub: CSUF562/DailyBreadPlusNine)"},
    )
    try:
        with urlopen(request, timeout=25) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as exc:  # network/API boundary
        raise RuntimeError(f"NASA/JPL Horizons request failed for body {body_id}: {exc}") from exc

    result = payload.get("result", "")
    if "$$SOE" not in result or "$$EOE" not in result:
        error = payload.get("error") or "Horizons response did not contain an ephemeris table"
        raise RuntimeError(f"NASA/JPL Horizons error for body {body_id}: {error}")

    before, table_and_after = result.split("$$SOE", 1)
    table, _ = table_and_after.split("$$EOE", 1)
    data_lines = [line.strip() for line in table.splitlines() if line.strip()]
    if not data_lines:
        raise RuntimeError(f"NASA/JPL Horizons returned no data row for body {body_id}")

    # Horizons prints a CSV heading immediately before $$SOE. Search backward
    # for the heading containing a field we explicitly requested.
    header_line = None
    for line in reversed(before.splitlines()):
        if "ObsEcLon" in line or "Illu%" in line or "S-O-T" in line:
            header_line = line.strip()
            break
    if not header_line:
        raise RuntimeError(f"Could not locate Horizons CSV header for body {body_id}")

    header = next(csv.reader(io.StringIO(header_line)))
    values = next(csv.reader(io.StringIO(data_lines[0])))
    header = [item.strip() for item in header]
    values = [item.strip() for item in values]

    # Some Horizons CSV rows may include trailing empty fields. Zip only known columns.
    row = {key: values[idx] if idx < len(values) else "" for idx, key in enumerate(header)}
    return row


def _float_field(row: Dict[str, str], *candidates: str) -> float:
    for key in candidates:
        if key in row and row[key] not in {"", "n.a.", "N/A"}:
            try:
                return float(row[key])
            except ValueError:
                continue
    raise RuntimeError(f"Horizons response missing numeric field from {candidates}")


def _angular_separation(a: float, b: float) -> float:
    diff = abs(a - b) % 360.0
    return min(diff, 360.0 - diff)


def _planet_positions(target_date: date) -> Dict[str, float]:
    positions: Dict[str, float] = {}
    for name, body_id in BODIES.items():
        quantities = "10,24,31" if name == "Moon" else "31"
        row = _fetch_horizons_row(body_id, target_date.isoformat(), quantities)
        positions[name] = _float_field(row, "ObsEcLon", "ObsEcLon(deg)") % 360.0
    return positions


def observations_for(target_date: date) -> List[SkyObservation]:
    """Return verifiable geocentric sky facts for 12:00 UTC on target_date.

    Facts include apparent ecliptic longitude for the Sun, Moon, and planets,
    lunar illumination, and selected angular separations. No zodiac signs or
    astrological meanings are produced here.
    """

    positions = _planet_positions(target_date)
    observations: List[SkyObservation] = []

    for name in BODIES:
        observations.append(
            SkyObservation(
                label=f"{name} apparent geocentric ecliptic longitude",
                value=f"{positions[name]:.3f}° at 12:00 UTC",
                source=JPL_HORIZONS,
            )
        )

    moon_row = _fetch_horizons_row(BODIES["Moon"], target_date.isoformat(), "10,24,31")
    illuminated = _float_field(moon_row, "Illu%", "Illu% ")
    observations.append(
        SkyObservation(
            label="Moon illuminated fraction",
            value=f"{illuminated:.2f}% at 12:00 UTC",
            source=JPL_HORIZONS,
        )
    )

    # Report objective angular geometry that downstream astrology may interpret.
    pairs = [
        ("Sun", "Moon"),
        ("Sun", "Mercury"),
        ("Sun", "Venus"),
        ("Sun", "Mars"),
        ("Sun", "Jupiter"),
        ("Sun", "Saturn"),
        ("Moon", "Mercury"),
        ("Moon", "Venus"),
        ("Moon", "Mars"),
        ("Moon", "Jupiter"),
        ("Moon", "Saturn"),
    ]
    for first, second in pairs:
        separation = _angular_separation(positions[first], positions[second])
        observations.append(
            SkyObservation(
                label=f"{first}-{second} geocentric angular separation",
                value=f"{separation:.3f}°",
                source=JPL_HORIZONS,
            )
        )

    observations.append(
        SkyObservation(
            label="ephemeris snapshot",
            value=f"NASA/JPL Horizons geocentric observer table for {target_date.isoformat()} 12:00 UTC",
            source=JPL_HORIZONS,
        )
    )
    return observations
