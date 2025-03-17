import pydre.core
import polars as pl
import pytest
import pydre.metrics
import pydre.metrics.common
import pydre.project
from pathlib import Path


FIXTURE_DIR = Path(__file__).parent.resolve() / "test_data"

@pytest.mark.datafiles(FIXTURE_DIR / "good_projectfiles" / "test_time_roi_2.toml")
def test_time_roi_1(datafiles):
    proj = pydre.project.Project(projectfilename=datafiles / "test_time_roi_2.toml", additional_data_paths=["C:\\Users\\aatchley\Documents\\test_folder\\Experimenter_1_Practice_1734102921.dat"])
    proj.processDatafiles(12)

@pytest.mark.datafiles(FIXTURE_DIR / "good_projectfiles" / "test_time_roi_1.toml")
def test_time_roi_2(datafiles):
    proj = pydre.project.Project(projectfilename=datafiles / "test_time_roi_1.toml", additional_data_paths=["C:\\Users\\aatchley\Documents\\test_folder\\Experimenter_1_Practice_1734102921.dat"])
    print(proj)
    proj.processDatafiles(12)

@pytest.mark.datafiles(FIXTURE_DIR / "good_projectfiles" / "test_time_roi_2.toml")
def test_time_roi(datafiles):
    proj = pydre.project.Project(projectfilename=datafiles / "test_time_roi_2.toml", additional_data_paths=["C:\\Users\\aatchley\Documents\\test_folder\\Experimenter_1_Practice_1734102921.dat"])
    proj.processDatafiles(12)

@pytest.mark.datafiles(FIXTURE_DIR / "good_projectfiles" / "test_time_roi_1.toml")
def test_time_roi_fail_2(datafiles):
    with pytest.raises(pl.exceptions.NoDataError):
        proj = pydre.project.Project(projectfilename=datafiles / "test_time_roi_1.toml", additional_data_paths=["C:\\Users\\aatchley\\Documents\\pydre\\tests\\test_data\\test_datfiles\\Experimenter_S1_Tutorial_11002233.dat"])
        print(proj)
        proj.processDatafiles(12)

@pytest.mark.datafiles(FIXTURE_DIR / "good_projectfiles" / "test_time_roi_2.toml")
def test_time_roi_fail_2(datafiles):
    with pytest.raises(pl.exceptions.NoDataError):
        proj = pydre.project.Project(projectfilename=datafiles / "test_time_roi_2.toml", additional_data_paths=["C:\\Users\\aatchley\\Documents\\test_folder\\Experimenter_1_Accommodation Drive_1734102446.dat"])
        print(proj)
        proj.processDatafiles(12)

