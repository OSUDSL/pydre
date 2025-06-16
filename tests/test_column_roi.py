import pydre.core
import pydre.rois
import polars as pl
import pytest
from pathlib import Path

# Define the directory that contains test CSV data
FIXTURE_DIR = Path(__file__).parent.resolve() / "test_data" / "test_roi_files"

@pytest.mark.datafiles(FIXTURE_DIR / "test_column_roi.csv")  # This file is not used in this test but kept for consistency
def test_column_roi_split(datafiles):
    # Create sample drive data with a column "Task" used for ROI
    df = pl.DataFrame({
        "SimTime": [0, 1, 2, 3, 4, 5],
        "Task": [1, 1, 2, 2, 3, 3],
        "Speed": [10, 20, 30, 40, 50, 60]
    })

    # Metadata is required by DriveData, even if simple
    metadata = {"ParticipantID": "Test01"}
    drive_data = pydre.core.DriveData()
    drive_data.data = df
    drive_data.metadata = metadata
    drive_data.sourcefilename = "dummy"

    # Instantiate a ColumnROI using the "Task" column
    roi = pydre.rois.ColumnROI("Task")
    results = roi.split(drive_data)

    # Expecting 3 distinct ROIs (1, 2, 3)
    assert len(results) == 3

    # ROI labels should match
    roi_names = {d.roi for d in results}
    assert roi_names == {"1", "2", "3"}

    # Each result should be a valid DriveData object
    for d in results:
        assert isinstance(d, pydre.core.DriveData)
