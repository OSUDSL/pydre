"""
Minimal skeleton for gaze cutout/angle metrics.
Goal: measure time/ratio/violations when gaze is outside a cutout angle,
optionally only when off a given object (FILTERED_GAZE_OBJ_NAME != target).
"""

import polars as pl
from pydre.core import ColumnsMatchError
from pydre.metrics import registerMetric


_REQUIRED_COLS = [
    "SimTime",                  # time base (s)
    "GAZE_HEADING",             # yaw (deg)
    "GAZE_PITCH",               # pitch (deg)
    "FILTERED_GAZE_OBJ_NAME",   # world object label or null
]

# TODO(questions):
# - confirm angle model: cone_dist = sqrt(yaw^2 + pitch^2) in degrees?
# - default cutout half-angle (deg) OK at 5.0?
# - time base = SimTime (not RealTime/MediaTime)?
# - off-target rule: count only when OBJ_NAME != target (or null)?

def _prepare(df: pl.DataFrame, *, angle_deg: float, target: str | None,
             time_col: str, heading_col: str, pitch_col: str, obj_col: str) -> pl.DataFrame:
    """
    TODO(impl):
    - cone_dist = sqrt(heading^2 + pitch^2)
    - outside = cone_dist > angle_deg
    - off_target = True if no target; else (obj is null) or (obj != target)
    - mask = outside & off_target
    - dt = next(SimTime) - SimTime (last row -> 0)
    - return df with columns: mask (bool), dt (float)
    """
    return df  # placeholder

@registerMetric("gazeCutoutAngleDuration")
@ColumnsMatchError(_REQUIRED_COLS)
def gaze_cutout_angle_duration(
    df: pl.DataFrame,
    *, angle_deg: float = 5.0, target: str | None = None,
    time_col: str = "SimTime", heading_col: str = "GAZE_HEADING",
    pitch_col: str = "GAZE_PITCH", obj_col: str = "FILTERED_GAZE_OBJ_NAME",
) -> float:
    """
    TODO(impl): sum(dt) over mask==True.
    """
    _ = _prepare(df, angle_deg=angle_deg, target=target,
                 time_col=time_col, heading_col=heading_col,
                 pitch_col=pitch_col, obj_col=obj_col)
    return 0.0  # placeholder

@registerMetric("gazeCutoutAngleRatio")
@ColumnsMatchError(_REQUIRED_COLS)
def gaze_cutout_angle_ratio(
    df: pl.DataFrame,
    *, angle_deg: float = 5.0, target: str | None = None,
    time_col: str = "SimTime", heading_col: str = "GAZE_HEADING",
    pitch_col: str = "GAZE_PITCH", obj_col: str = "FILTERED_GAZE_OBJ_NAME",
) -> float:
    """
    TODO(impl): sum(dt where mask)/sum(dt total), guard total==0.
    """
    _ = _prepare(df, angle_deg=angle_deg, target=target,
                 time_col=time_col, heading_col=heading_col,
                 pitch_col=pitch_col, obj_col=obj_col)
    return 0.0  # placeholder

@registerMetric("gazeCutoutAngleViolations")
@ColumnsMatchError(_REQUIRED_COLS)
def gaze_cutout_angle_violations(
    df: pl.DataFrame,
    *, angle_deg: float = 5.0, target: str | None = None,
    time_col: str = "SimTime", heading_col: str = "GAZE_HEADING",
    pitch_col: str = "GAZE_PITCH", obj_col: str = "FILTERED_GAZE_OBJ_NAME",
) -> int:
    """
    TODO(impl): count segments: mask True with previous False (run starts).
    """
    _ = _prepare(df, angle_deg=angle_deg, target=target,
                 time_col=time_col, heading_col=heading_col,
                 pitch_col=pitch_col, obj_col=obj_col)
    return 0  # placeholder
