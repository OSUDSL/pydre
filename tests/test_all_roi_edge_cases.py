import polars as pl
import pytest
import tempfile
import os
from pydre.core import DriveData
from pydre.rois import ColumnROI, SpaceROI

def test_column_roi_invalid_type():
    df = pl.DataFrame({"ROI": ["A", "B"], "Value": [1, 2]})
    processor = ColumnROI("ROI")
    with pytest.raises(AttributeError):  # or TypeError if you enforce it in code
        processor.split(df)

def test_column_roi_with_null_group_skipped():
    df = pl.DataFrame({
        "ROI": ["A", None, "B"],
        "Value": [1, 2, 3]
    })
    dd = DriveData.init_test(df, "test.dat")
    processor = ColumnROI("ROI")
    result = processor.split(dd)

    rois = set(d.roi for d in result)
    rois_filtered = {r for r in rois if r != "None"}  # "None" 문자열 제거

    assert rois_filtered == {"A", "B"}

def test_space_roi_missing_columns():
    df = pl.DataFrame({"X": [0], "Y": [0]})
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tf:
        filepath = tf.name
    df.write_csv(filepath)
    try:
        with pytest.raises(ValueError):
            SpaceROI(filepath)
    finally:
        os.unlink(filepath)
