import polars as pl
import pytest
from pydre.core import DriveData
from pydre.filters.gazeangle import gazeAnglePreProcessing
from pydre.metrics import gazeanglecutout


@pytest.fixture
def sample_drivedata():
    """
    Creates a DriveData object with synthetic gaze data.
    Heading/pitch values are in radians, DatTime in seconds.
    """
    df = pl.DataFrame({
        "DatTime": [0.0, 1.0, 2.0, 3.0, 4.0],
        "GAZE_HEADING": [0.02, 0.1, 0.12, 0.02, 0.09],
        "GAZE_PITCH": [0.01, 0.04, 0.09, 0.02, 0.07],
        "FILTERED_GAZE_OBJ_NAME": ["target", "target", None, "target", None],
    })

    d = DriveData()
    d.data = df
    return d


def test_gazeangle_filter_outputs(sample_drivedata):
    """
    The gazeangle filter should produce expected columns and reasonable values.
    """
    out = gazeAnglePreProcessing(sample_drivedata)

    # verify added columns
    for col in ["gaze_angle", "gaze_cutout", "off_target"]:
        assert col in out.data.columns, f"Missing column: {col}"

    # all gaze angles should be >= 0
    assert (out.data["gaze_angle"] >= 0).all()

    # there should be at least one cutout True and one False
    assert out.data["gaze_cutout"].any() and not out.data["gaze_cutout"].all()


def test_gazeanglecutout_metrics(sample_drivedata):
    """
    Check that gazeanglecutout metrics produce consistent, interpretable results.
    """
    # Apply filter first
    filtered = gazeAnglePreProcessing(sample_drivedata)

    # 1) Duration should be > 0
    duration = gazeanglecutout.gazeCutoutAngleDuration(filtered)
    assert isinstance(duration, float)
    assert duration >= 0.0

    # 2) Ratio should be between 0 and 1
    ratio = gazeanglecutout.gazeCutoutAngleRatio(filtered)
    assert 0.0 <= ratio <= 1.0

    # 3) Violations should be an integer >= 0
    violations = gazeanglecutout.gazeCutoutAngleViolations(filtered)
    assert isinstance(violations, int)
    assert violations >= 0

    # Sanity relationship: if no off-target frames exist, duration must be 0
    df = filtered.data.with_columns(pl.lit(False).alias("off_target"))
    filtered.data = df
    assert gazeanglecutout.gazeCutoutAngleDuration(filtered) == 0.0


def test_empty_dataframe_behavior():
    """
    Empty data should not raise and should return 0 metrics.
    """
    d = DriveData()
    d.data = pl.DataFrame({
        "DatTime": [],
        "gaze_cutout": [],
        "off_target": [],
    })

    assert gazeanglecutout.gazeCutoutAngleDuration(d) == 0.0
    assert gazeanglecutout.gazeCutoutAngleRatio(d) == 0.0
    assert gazeanglecutout.gazeCutoutAngleViolations(d) == 0
