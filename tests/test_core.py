from pathlib import Path
import pytest
import polars as pl
from pydre.core import DriveData, ColumnsMatchError

FIXTURE_DIR = Path(__file__).parent.resolve() / "test_data"


@pytest.mark.datafiles(
    FIXTURE_DIR / "test_datfiles" / "ExampleProject_Sub_1_Drive_1.dat"
)
def test_init_old_rti(datafiles):
    """Test initialization of DriveData using old RTI format."""
    file_path = datafiles / "ExampleProject_Sub_1_Drive_1.dat"

    drive_data = DriveData.init_old_rti(file_path)

    assert drive_data.sourcefilename == file_path
    assert drive_data.sourcefiletype == "old SimObserver"
    assert drive_data.metadata["ParticipantID"] == "1"
    assert drive_data.metadata["DriveID"] == "1"


@pytest.mark.datafiles(
    FIXTURE_DIR / "test_datfiles" / "ExampleProject_Sub_1_Drive_1.dat"
)
def test_init_test(datafiles):
    """Test initialization with test data."""
    df = pl.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
    file_path = datafiles / "ExampleProject_Sub_1_Drive_1.dat"

    drive_data = DriveData.init_test(df, file_path)

    assert drive_data.sourcefilename == file_path
    assert drive_data.data.equals(df)


def test_init_from_existing():
    """Test creating DriveData from existing DriveData."""
    original = DriveData()
    original.sourcefilename = Path("test.dat")
    original.sourcefiletype = "test"
    original.roi = "test_roi"
    original.metadata = {"key": "value"}

    # Test with default parameters
    copy = DriveData(original)
    assert copy.sourcefilename == original.sourcefilename
    assert copy.sourcefiletype == original.sourcefiletype
    assert copy.roi == original.roi
    assert copy.metadata == original.metadata

    # Test with new data
    new_df = pl.DataFrame({"A": [1, 2, 3]})
    copy_with_data = DriveData(original, new_df)
    assert copy_with_data.data.equals(new_df)


@pytest.mark.datafiles(
    FIXTURE_DIR / "test_datfiles" / "ExampleProject_Sub_1_Drive_1.dat"
)
def test_load_datfile(datafiles):
    """Test loading data from datfile."""
    file_path = datafiles / "ExampleProject_Sub_1_Drive_1.dat"

    drive_data = DriveData.init_old_rti(file_path)
    drive_data.loadData()

    assert not drive_data.data.is_empty()
    assert "VidTime" in drive_data.data.columns
    assert "SimTime" in drive_data.data.columns


@pytest.mark.datafiles(
    FIXTURE_DIR / "test_datfiles" / "ExampleProject_Sub_1_Drive_1.dat"
)
def test_copy_metadata(datafiles):
    """Test copying metadata between DriveData objects."""
    file_path = datafiles / "ExampleProject_Sub_1_Drive_1.dat"

    source = DriveData.init_old_rti(file_path)
    source.roi = "test_roi"
    source.metadata["TestKey"] = "TestValue"

    target = DriveData()
    target.copyMetaData(source)

    assert target.sourcefilename == source.sourcefilename
    assert target.sourcefiletype == source.sourcefiletype
    assert target.roi == source.roi
    assert target.metadata == source.metadata


@pytest.mark.datafiles(
    FIXTURE_DIR / "test_datfiles" / "ExampleProject_Sub_1_Drive_1.dat"
)
def test_check_columns(datafiles):
    """Test column validation."""
    file_path = datafiles / "ExampleProject_Sub_1_Drive_1.dat"

    drive_data = DriveData.init_old_rti(file_path)
    drive_data.loadData()

    # Should not raise for existing columns
    drive_data.checkColumns(["VidTime", "SimTime"])

    # Should raise for missing columns
    with pytest.raises(ColumnsMatchError) as exc_info:
        drive_data.checkColumns(["NonExistentColumn"])

    assert "NonExistentColumn" in str(exc_info.value)
    assert "NonExistentColumn" in exc_info.value.missing_columns


def test_columns_match_error():
    """Test ColumnsMatchError class."""
    error = ColumnsMatchError("Custom message", ["col1", "col2"])
    assert "Custom message" in str(error)
    assert error.missing_columns == ["col1", "col2"]

    # Test default message generation
    error = ColumnsMatchError("", ["col3", "col4"])
    assert "Columns in DriveData object not as expected" in str(error)
    assert "col3" in str(error)
    assert "col4" in str(error)
