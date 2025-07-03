from __future__ import annotations

"""Utility functions for filtering noisy GPS coordinates.

Implements two simple yet very effective steps that remove most of the jitter
observed on low-cost GNSS receivers:

1.  Gross-error rejection (distance / speed thresholding)
2.  Exponential Moving Average (a first-order low-pass filter)

The logic is intentionally stateless - the calling code is expected to provide
previously accepted coordinates and their timestamp (stored e.g. in Redis).
"""

from datetime import datetime
from typing import Optional, Tuple

from app.utils.eta import calc_distance  # Haversine distance in metres
from app.core.point import Coord

import numpy as np
import pyproj


# --------------------------------------------------------------------------------------
# Tuning constants – adjust per project / hardware characteristics
# --------------------------------------------------------------------------------------
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
ALPHA = 0.2  # EMA coefficient (0 < α ≤ 1). 0.4 ⇒ ~40 % of new reading. 
# α close to 1 → hugs the raw data (little smoothing, low lag).
# α close to 0 → very smooth but lags behind quick changes.
MAX_SPEED_MPS = 40  # Reject fixes that imply speed > 40 m/s  (≈144 km/h)


def filter_point(
    new_lat: float,
    new_lon: float,
    prev_lat: Optional[float],
    prev_lon: Optional[float],
    prev_time_str: Optional[str],
    *,
    alpha: float = ALPHA,
    max_speed: float = MAX_SPEED_MPS,
) -> Tuple[float, float, bool]:
    """Apply gross-error rejection **and** EMA smoothing to a GPS fix.

    Parameters
    ----------
    new_lat, new_lon
        Raw coordinates received from the GPS module.
    prev_lat, prev_lon
        Last accepted (already filtered) location or *None* if this is the first fix.
    prev_time_str
        Timestamp of the previous accepted fix in ``DATETIME_FORMAT`` or *None*.
    alpha
        Weight of the *current* reading in EMA. 0 → heavily smoothed, 1 → no smoothing.
    max_speed
        Maximum allowed speed in *m/s* between consecutive fixes.

    Returns
    -------
    (lat_f, lon_f, accepted)
        ``lat_f`` / ``lon_f`` are either the filtered coordinates (if *accepted* is *True*)
        or the previous ones (if fix rejected).
    """

    # ------------------------------------------------------------------
    # First fix – nothing to compare / smooth against, accept as-is.
    # ------------------------------------------------------------------
    if prev_lat is None or prev_lon is None or prev_time_str is None:
        return new_lat, new_lon, True

    prev_coord = Coord(lat=prev_lat, lon=prev_lon)
    curr_coord = Coord(lat=new_lat, lon=new_lon)

    # ------------------------------------------------------------------
    # 1. Gross-error rejection
    # ------------------------------------------------------------------
    distance = calc_distance(prev_coord, curr_coord)  # metres

    try:
        dt = (
            datetime.now() - datetime.strptime(prev_time_str, DATETIME_FORMAT)
        ).total_seconds()
        if dt <= 0:  # protect against identical / invalid timestamps
            dt = 1e-6
        speed = distance / dt  # m/s
    except Exception:
        # Malformed timestamp – fall back to distance check only
        speed = 0.0

    if speed > max_speed:
        return prev_lat, prev_lon, False

    # ------------------------------------------------------------------
    # 2. Exponential Moving Average (EMA)
    # ------------------------------------------------------------------
    wgs84   = 4326
    utm43n  = 32643          # Kyrgyzstan–Bishkek area
    fwd = pyproj.Transformer.from_crs(wgs84, utm43n, always_xy=True).transform
    inv = pyproj.Transformer.from_crs(utm43n, wgs84, always_xy=True).transform
    
    new_x, new_y = fwd(new_lon, new_lat)
    prev_x, prev_y = fwd(prev_lon, prev_lat)
    
    # Apply EMA to the projected coordinates
    x_smooth = alpha * new_x + (1.0 - alpha) * prev_x
    y_smooth = alpha * new_y + (1.0 - alpha) * prev_y
    
    lat_smooth, lon_smooth = inv(x_smooth, y_smooth)

    return lat_smooth, lon_smooth, True 


# NOTE: When you might not want plain EMA:
# If you need velocity as well as position, a Kalman filter keeps both in the state vector.
# If you must obey vehicle kinematics (e.g., cannot jump sideways), EMA is still purely mathematical; KF or particle filters enforce motion constraints.
