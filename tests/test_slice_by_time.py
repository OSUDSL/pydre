import polars as pl
import pytest
from pydre.rois import sliceByTime

def test_slice_by_time_invalid_column():
    df = pl.DataFrame({
        "WrongTime": [0, 1, 2]
    })

    with pytest.raises(Exception):  # ColumnNotFoundError or general
        sliceByTime(0, 1, "NoSuchColumn", df)