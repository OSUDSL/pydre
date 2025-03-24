import pydre.core
import polars as pl
import pytest
import pydre.metrics
import pydre.metrics.common
import pydre.project
import pydre.rois
from pathlib import Path


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