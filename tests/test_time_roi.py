import pydre.core
import polars as pl
import pytest
import pydre.metrics
import pydre.metrics.common
import pydre.project
import pydre.rois
from pathlib import Path
from pydre.core import DriveData
from pydre.rois import TimeROI


FIXTURE_DIR = Path(__file__).parent.resolve() / "test_data"


def test_parse_timestamp():
    hr = 1
    min = 15
    sec = 10
    assert pydre.rois.TimeROI.parseTimeStamp("1:15:10") == (sec + min * 60 + hr * 60 * 60)

    hr = 12
    min = 12
    sec = 0
    assert pydre.rois.TimeROI.parseTimeStamp("12:12:00") == (sec + min * 60 + hr * 60 * 60)

    min = 12
    sec = 59
    assert pydre.rois.TimeROI.parseTimeStamp("12:59") == (sec + min * 60)
    assert pydre.rois.TimeROI.parseTimeStamp("12:59") == (sec + min * 60)

    min = 0
    sec = 1
    assert pydre.rois.TimeROI.parseTimeStamp("00:01") == (sec + min * 60)


@pytest.mark.datafiles(FIXTURE_DIR / "test_roi_files")
def test_make_time_roi_1(datafiles):
    new_roi = pydre.rois.TimeROI(datafiles / "test_time_1.csv")
    assert new_roi.rois == {'roi_1': {'time_end': 540, 'time_start': 480}, 'roi_2': {'time_end': 240, 'time_start': 180}}
    assert isinstance(new_roi, pydre.rois.TimeROI)


@pytest.mark.datafiles(FIXTURE_DIR / "test_roi_files")
def test_make_time_roi_1(datafiles):
    new_roi = pydre.rois.TimeROI(datafiles / "test_time_2.csv")
    assert new_roi.rois == {'roi_1': {'ScenarioName': 'Practice', 'time_end': 180, 'time_start': 0}, 'roi_2': {'ScenarioName': 'Practice', 'time_end': 300, 'time_start': 180}}
    assert isinstance(new_roi, pydre.rois.TimeROI)


def test_slice_by_time_with_invalid_column():
    df = pl.DataFrame({
        "SimTime": [0.1, 0.2, 0.3]
    })

    result = pydre.rois.sliceByTime(0.0, 1.0, "NotAColumn", df)
    assert result.equals(df)


def test_parse_timestamp_invalid_format():
    with pytest.raises(ValueError):
        TimeROI.parseTimeStamp("invalid_format")


def test_slice_by_time_column_missing_logs_error(caplog):
    df = pl.DataFrame({"NotSimTime": [0.1, 0.2]})
    with caplog.at_level("ERROR"):
        result = pydre.rois.sliceByTime(0.0, 1.0, "SimTime", df)
        assert result.equals(df)
        assert "Problem in applying Time ROI" in caplog.text


def test_time_roi_with_metadata_mismatch_skips_roi(tmp_path):
    roi_data = pl.DataFrame({
        "ROI": ["Practice1"],
        "time_start": ["00:00"],
        "time_end": ["00:10"],
        "ScenarioName": ["Training"]
    })
    path = tmp_path / "roi.csv"
    roi_data.write_csv(str(path))

    dd = DriveData.init_test(pl.DataFrame({"SimTime": [1.0]}), "drive.dat")
    dd.metadata = {"ScenarioName": "Test"}  # No match

    roi = TimeROI(str(path))
    results = roi.split(dd)
    assert results == []  # ROI should be skipped


def test_slice_by_time_column_missing_returns_original_df_and_logs(caplog):
    df = pl.DataFrame({
        "OtherTime": [0.1, 0.2, 0.3],
        "Value": [10, 20, 30]
    })

    with caplog.at_level("ERROR"):
        result = pydre.rois.sliceByTime(0.0, 1.0, "SimTime", df)
        assert result.to_dicts() == df.to_dicts()
        assert "problem in applying time roi" in caplog.text.lower()


def test_time_roi_split_warns_on_invalid_range(caplog):
    df = pl.DataFrame({
        "SimTime": [0.0, 0.1, 0.2, 0.3],
        "Event": ["a", "b", "c", "d"]
    })
    dd = DriveData.init_test(df, "sim.dat")

    roi = TimeROI.from_ranges(ranges=[(1.0, 2.0)], column="SimTime")
    roi.rois_meta = []
    roi.timecol = "SimTime"

    roi.rois = pl.DataFrame({
        "roi": ["invalid_range"],
        "time_start": [1.0],
        "time_end": [2.0]
    })

    class MockDictLikeDataFrame:
        def __init__(self, df):
            self.df = df

        def copy(self):
            return MockDictLikeDataFrame(self.df.clone())

        def items(self):
            return [
                (i, row)
                for i, row in enumerate(self.df.iter_rows(named=True))
            ]

        def __getitem__(self, key):
            return self.df[key]

        def __delitem__(self, key):
            mask = pl.Series([i for i in range(len(self.df)) if i != key])
            self.df = self.df[mask]

    roi.rois = MockDictLikeDataFrame(roi.rois)

    with caplog.at_level("WARNING"):
        list(roi.split(dd))

    assert any("ROI fails to qualify" in msg for msg in caplog.text.splitlines())

