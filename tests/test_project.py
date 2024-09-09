from pathlib import Path
import pytest
import pydre.project
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


@pytest.mark.datafiles(
    FIXTURE_DIR / "good_projectfiles" / "test1_pf.json",
    FIXTURE_DIR / "good_projectfiles" / "test1_pf.toml",
)
def test_project_projequiv(datafiles):
    proj_json = pydre.project.Project(datafiles / "test1_pf.json")
    proj_toml = pydre.project.Project(datafiles / "test1_pf.toml")
    assert proj_json == proj_toml
