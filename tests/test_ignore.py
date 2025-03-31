from pathlib import Path
import pytest
import pydre.project
import polars as pl
import polars.testing

from loguru import logger

FIXTURE_DIR = Path(__file__).parent.resolve() / "test_data"

@pytest.mark.datafiles(FIXTURE_DIR / "good_projectfiles" / "test_ignore_1.toml")
def test_ignore_1(datafiles):
    proj = pydre.project.Project(datafiles / "test_ignore_1.toml")
    assert len(proj.filelist) == 8
    assert isinstance(proj, pydre.project.Project)

@pytest.mark.datafiles(FIXTURE_DIR / "good_projectfiles" / "test_ignore_2.toml")
def test_ignore_1(datafiles):
    proj = pydre.project.Project(datafiles / "test_ignore_2.toml")
    assert len(proj.filelist) == 6
    assert isinstance(proj, pydre.project.Project)