from pathlib import Path
import pytest
import polars as pl
from pydre.core import DriveData
from pydre.project import Project

FIXTURE_DIR = Path(__file__).parent.resolve() / "test_data"

@pytest.mark.datafiles(
    FIXTURE_DIR / "good_projectfiles" / "test_infer_schema.toml",
    FIXTURE_DIR / "test_datfiles" / "test_infer_schema.dat",
)
def test_infer_schema_sufficient_length(datafiles):
    """Test that a sufficient infer_schema_length (5) correctly infers schema and processes data."""
    toml_path = datafiles / "test_infer_schema.toml"
    resolved_data_file = str(
        datafiles / "test_infer_schema.dat"
    )
    proj = Project(toml_path, additional_data_paths=[resolved_data_file])

    result = proj.processDatafiles()

    # Verify that results were generated successfully
    assert result is not None
    assert isinstance(result, pl.DataFrame)
    assert result.height > 0

    # Verify that the meanXPos metric was calculated as a float
    assert result['meanXPos'].is_not_null().all()


@pytest.mark.datafiles(
    FIXTURE_DIR / "good_projectfiles" / "test_infer_schema_short.toml",
    FIXTURE_DIR / "test_datfiles" / "test_infer_schema.dat",
)
def test_infer_schema_insufficient_length(datafiles):
    """Test that an insufficient infer_schema_length (2) causes schema inference errors."""
    toml_path = datafiles / "test_infer_schema_short.toml"
    resolved_data_file = str(
        datafiles / "test_infer_schema.dat"
    )
    proj = Project(toml_path, additional_data_paths=[resolved_data_file])

    result = proj.processDatafiles()

    assert result is not None
    assert isinstance(result, pl.DataFrame)
    assert result.height > 0

    # Verify that the meanXPos metric was incorrectly calculated as null due to schema inference failure
    assert result['meanXPos'].is_null().all()

