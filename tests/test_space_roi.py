import pydre.core
import pydre.rois
import polars as pl
import pytest
import tempfile
from pathlib import Path
from pydre.core import DriveData
from pydre.rois import SpaceROI
from pydre.rois import TimeROI

# Define the directory that contains test CSV data
FIXTURE_DIR = Path(__file__).parent.resolve() / "test_data" / "test_roi_files"

@pytest.mark.datafiles(FIXTURE_DIR / "test_space_roi.csv")
def test_space_roi_split(datafiles):
    # Create the SpaceROI object from the test ROI file
    roi = pydre.rois.SpaceROI(datafiles / "test_space_roi.csv")

    # Construct sample drive data that includes positions within defined ROI zones
    df = pl.DataFrame({
        "XPos": [10.0, 15.0, 25.0],
        "YPos": [10.0, 15.0, 25.0],
        "Speed": [5.0, 6.0, 7.0]
    })

    # Basic metadata and fake filename for the DriveData object
    metadata = {"ParticipantID": "S01"}
    drive_data = pydre.core.DriveData()
    drive_data.data = df
    drive_data.metadata = metadata
    drive_data.sourcefilename = "fake"

    # Split the data based on ROI regions
    results = roi.split(drive_data)

    # Ensure each result is a valid DriveData object with a region assigned
    assert all(isinstance(d, pydre.core.DriveData) for d in results)

    # Each region should have some data in it
    assert all(d.data.height > 0 for d in results)

    # ROI names should be assigned
    assert all(hasattr(d, "roi") for d in results)

def test_spaceroi_invalid_columns():
    with tempfile.NamedTemporaryFile(suffix=".csv", mode="w+", delete=False) as f:
        f.write("wrong,columns\\n1,2\\n")
        f.flush()
        with pytest.raises(ValueError):
            _ = SpaceROI(f.name)

def test_space_roi_with_missing_coordinate_keys():
    df = pl.DataFrame({
        "XPos": [1.0], "YPos": [1.0], "Speed": [5.0]
    })
    data = DriveData.init_test(df, "bad.dat")

    roi_df = pl.DataFrame({
        "roi": ["bad_roi"],
        "X1": [0], "X2": [2]
    })

    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".csv") as f:
        roi_df.write_csv(f.name)

    with pytest.raises(ValueError):
        _ = SpaceROI(f.name)

def test_time_roi_with_metadata_filtering():
    roi_df = pl.DataFrame({
        "ROI": ["roi1"],
        "time_start": ["00:00"],
        "time_end": ["00:10"],
        "ScenarioName": ["Practice"]
    })

    dd = DriveData.init_test(pl.DataFrame({"SimTime": [0.1, 0.2]}), "drive.dat")
    dd.metadata = {"ScenarioName": "Test"}

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".csv", delete=False) as f:
        roi_df.write_csv(f.name)
        roi = TimeROI(f.name)
        result = roi.split(dd)

    assert result == []


def test_space_roi_rectangle_out_of_bounds_logs_warning(tmp_path, caplog):
    roi_df = pl.DataFrame({
        "roi": ["offbounds"],
        "X1": [1000], "X2": [2000],
        "Y1": [1000], "Y2": [2000]
    })
    path = tmp_path / "roi.csv"
    roi_df.write_csv(str(path))

    df = pl.DataFrame({
        "XPos": [0, 1], "YPos": [0, 1], "Speed": [10, 15]
    })
    dd = DriveData.init_test(df, "drive.dat")
    dd.metadata["ParticipantID"] = "TestSubject"

    with caplog.at_level("WARNING"):
        roi = SpaceROI(str(path))
        result = roi.split(dd)

        assert len(result) == 1
        assert result[0].data.height == 0
        assert "no data" in caplog.text.lower()

def test_space_roi_invalid_type_logs_error(tmp_path, caplog):
    roi_df = pl.DataFrame({
        "roi": ["invalid"],
        "X1": ["not-a-number"],  # TypeError 유도
        "X2": [200],
        "Y1": [0], "Y2": [100]
    })
    path = tmp_path / "invalid_roi.csv"
    roi_df.write_csv(str(path))

    df = pl.DataFrame({"XPos": [10], "YPos": [20]})
    dd = DriveData.init_test(df, "test.dat")

    roi = SpaceROI(str(path))
    with caplog.at_level("ERROR"):
        result = roi.split(dd)
        assert result == []
        assert "bad datatype" in caplog.text.lower()