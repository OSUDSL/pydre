import pydre.core
import pydre.rois
import polars as pl
import pytest
from pathlib import Path

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
