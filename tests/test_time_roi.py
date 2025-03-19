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


@pytest.mark.datafiles(FIXTURE_DIR / "good_projectfiles" / "test_time_roi_2.toml")
def test_time_roi_1(datafiles):
    data_path = str(FIXTURE_DIR / "test_datfiles" / "Experimenter_S1_Tutorial_11002233.dat")
    proj = pydre.project.Project(projectfilename=datafiles / "test_time_roi_2.toml", additional_data_paths=[data_path])
    proj.processDatafiles(12)

@pytest.mark.datafiles(FIXTURE_DIR / "good_projectfiles" / "test_time_roi_1.toml")
def test_time_roi_2(datafiles):
    data_path = str(FIXTURE_DIR / "test_datfiles" / "Experimenter_S1_Tutorial_11002233.dat")
    proj = pydre.project.Project(projectfilename=datafiles / "test_time_roi_1.toml", additional_data_paths=[data_path])
    print(proj)
    proj.processDatafiles(12)

@pytest.mark.datafiles(FIXTURE_DIR / "good_projectfiles" / "test_time_roi_2.toml")
def test_time_roi(datafiles):
    data_path = str(FIXTURE_DIR / "test_datfiles" / "Experimenter_S1_Tutorial_11002233.dat")
    proj = pydre.project.Project(projectfilename=datafiles / "test_time_roi_2.toml", additional_data_paths=[data_path])
    proj.processDatafiles(12)

@pytest.mark.datafiles(FIXTURE_DIR / "good_projectfiles" / "test_time_roi_1.toml")
def test_time_roi_fail_2(datafiles):
    data_path = str(FIXTURE_DIR / "test_datfiles" / "Experimenter_S1_Tutorial_11002233.dat")
    with pytest.raises(pl.exceptions.NoDataError):
        proj = pydre.project.Project(projectfilename=datafiles / "test_time_roi_1.toml", additional_data_paths=[data_path])
        print(proj)
        proj.processDatafiles(12)

@pytest.mark.datafiles(FIXTURE_DIR / "good_projectfiles" / "test_time_roi_2.toml")
def test_time_roi_fail_2(datafiles):
    with pytest.raises(pl.exceptions.NoDataError):
        data_path = str(FIXTURE_DIR / "test_datfiles" / "Experimenter_S1_Tutorial_11002233.dat")
        proj = pydre.project.Project(projectfilename=datafiles / "test_time_roi_2.toml", additional_data_paths=[data_path])
        print(proj)
        proj.processDatafiles(12)

