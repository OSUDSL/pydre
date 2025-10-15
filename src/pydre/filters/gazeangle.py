import math
import polars as pl
import pydre.core
from pydre.core import ColumnsMatchError
from pydre.filters import registerFilter


@registerFilter()
def gazeangle(
        drivedata: pydre.core.DriveData,
        half_angle_deg: float = 5.0,
        target_name: str | None = None
) -> pydre.core.DriveData:
    """
    Compute gaze angle magnitude and mark whether gaze is off-target (cutout).

    Parameters
    ----------
    drivedata : pydre.core.DriveData
        Input DriveData object containing raw gaze columns.
    half_angle_deg : float, optional
        Default cutout half-angle threshold, in degrees. Default is 5.0°.
        Note: eyetracking machine data is in radians, so this is converted internally.
    target_name : str | None, optional
        Optional target object name to check against FILTERED_GAZE_OBJ_NAME.

    Returns
    -------
    pydre.core.DriveData
        DriveData with new columns:
            - gaze_angle : float (radians)
            - gaze_cutout : bool
            - off_target : bool
    """

    required_cols = [
        "DatTime",
        "GAZE_HEADING",
        "GAZE_PITCH",
        "FILTERED_GAZE_OBJ_NAME"
    ]

    if not all(col in drivedata.data.columns for col in required_cols):
        raise ColumnsMatchError(f"Missing one or more required columns: {required_cols}")

    df = drivedata.data

    # Using sqrt(yaw^2 + pitch^2), directly in radians
    df = df.with_columns(
        (pl.sqrt(pl.col("GAZE_HEADING") ** 2 + pl.col("GAZE_PITCH") ** 2))
        .alias("gaze_angle")
    )

    # Convert threshold from degrees to radians for comparison
    half_angle_rad = math.radians(half_angle_deg)

    df = df.with_columns(
        (pl.col("gaze_angle") > half_angle_rad).alias("gaze_cutout")
    )

    if target_name:
        off_target_mask = (
            (pl.col("FILTERED_GAZE_OBJ_NAME").is_null())
            | (pl.col("FILTERED_GAZE_OBJ_NAME") != target_name)
        )
    else:
        # If no specific target provided, consider None values only as off-target
        off_target_mask = pl.col("FILTERED_GAZE_OBJ_NAME").is_null()

    df = df.with_columns(off_target_mask.alias("off_target"))

    drivedata.data = df
    return drivedata