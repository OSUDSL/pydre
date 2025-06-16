import polars as pl
from pydre.core import DriveData
from pydre.rois import ColumnROI

def test_column_roi_with_null_group():
    df = pl.DataFrame({
        "ROI": ["A", None, "B"],
        "Value": [1, 2, 3]
    })
    dd = DriveData.init_test(df, "test.dat")
    processor = ColumnROI("ROI")
    result = processor.split(dd)

    cleaned_rois = set(d.roi for d in result if d.roi not in (None, "None"))
    assert cleaned_rois == {"A", "B"}
