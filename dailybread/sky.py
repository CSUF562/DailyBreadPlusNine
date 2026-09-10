"""Observed-sky layer for DailyBreadPlusNine.

The production adapter is intended to use NASA/JPL Horizons as the scientific
source of ephemeris facts. This module keeps scientific observations separate
from astrological interpretation.
"""

from __future__ import annotations

from datetime import date
from typing import List

from .model import SkyObservation, SourceRef


JPL_HORIZONS = SourceRef(
    name="NASA/JPL Horizons",
    reference="Solar System Dynamics ephemeris service",
    url="https://ssd.jpl.nasa.gov/horizons/",
)


def observations_for(target_date: date) -> List[SkyObservation]:
    """Return observed-sky facts for *target_date*.

    This first architecture pass deliberately returns a provenance marker
    instead of fabricating planetary positions. A live Horizons adapter will
    populate Sun, Moon, planetary longitudes, lunar phase, and angular
    relationships in the next implementation step.
    """

    return [
        SkyObservation(
            label="ephemeris_status",
            value=f"NASA/JPL Horizons lookup required for {target_date.isoformat()}",
            source=JPL_HORIZONS,
        )
    ]
