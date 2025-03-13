from pathlib import Path
import pytest
import pydre.project
import polars as pl
from loguru import logger

FIXTURE_DIR = Path(__file__).parent.resolve() / "test_data"


@pytest.mark.datafiles(FIXTURE_DIR / "good_projectfiles" / "test1_pf.json")
def test_project_loadjson(datafiles):
    proj = pydre.project.Project(datafiles / "test1_pf.json")
    assert isinstance(proj, pydre.project.Project)


@pytest.mark.datafiles(FIXTURE_DIR / "good_projectfiles" / "test1_pf.toml")
def test_project_loadtoml(datafiles):
    proj = pydre.project.Project(datafiles / "test1_pf.toml")
    assert isinstance(proj, pydre.project.Project)


def test_project_loadbadtoml():
    with pytest.raises(FileNotFoundError):
        proj = pydre.project.Project("doesnotexist.toml")


@pytest.mark.datafiles(
    FIXTURE_DIR / "good_projectfiles" / "test1_pf.json",
    FIXTURE_DIR / "good_projectfiles" / "test1_pf.toml",
)
def test_project_projequiv(datafiles):
    proj_json = pydre.project.Project(datafiles / "test1_pf.json")
    proj_toml = pydre.project.Project(datafiles / "test1_pf.toml")
    assert proj_json == proj_toml

@pytest.mark.datafiles(
    FIXTURE_DIR / "good_projectfiles",
    FIXTURE_DIR / "test_custom_metric",
    FIXTURE_DIR / "test_datfiles",
    keep_top_dir=True
)
def test_project_custom_metric(datafiles):
    resolved_data_file = str(datafiles / "test_datfiles" / "clvspectest_Sub_8_Drive_3.dat")
    proj = pydre.project.Project(datafiles / "good_projectfiles" / "custom_test.toml",
                                 additional_data_paths=[resolved_data_file])
    proj.processDatafiles(numThreads=2)

    expected_result = pl.DataFrame([{'ParticipantID': "8", 'UniqueID': "3", 'ScenarioName': 'Drive', 'DXmode': 'Sub', 'ROI': None, 'custom_test': 1387.6228702430055}])

    assert proj.results.equals(expected_result)



