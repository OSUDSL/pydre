<<<<<<< HEAD
import datetime

import numpy as np
import polars as pl
import polars.testing
import pytest

import pydre.core
from pydre.filters.common import (
    FixReversedRoadLinearLand,
    Jenks,
    numberBinaryBlocks,
    relativeBoxPos,
    removeDataInside,
    removeDataOutside,
    separateData,
    setinrange,
    SimTimeFromDatTime,
    trimPreAndPostDrive,
    writeToCSV,
    filetimeToDatetime,
    filterValuesBelow,
    mergeSplitFiletime,
    zscoreCol,
)
=======
import polars as pl
import polars.datatypes
import pytest
import pydre.core
import polars.testing

from pydre.filters.common import trimPreAndPostDrive
from pydre.filters.common import nullifyOutlier

>>>>>>> origin/R2DRV


def test_trim_pre_and_post_drive():
    # Create a sample Polars DataFrame with pre and post drive segments
    data = {
        "SimTime": [0, 1, 2, 3, 4, 5, 6, 7, 8],
        "Velocity": [0.0, 0.05, 0.2, 5.0, 6.0, 4.0, 0.08, 0.05, 0.0],
    }
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

    # Apply the filter with default threshold
    trimmed_dd = trimPreAndPostDrive(dd)

    # Expected result (indexes 2-5 where velocity > 0.1)
    expected_indices = [2, 3, 4, 5]
    expected_df = df[expected_indices]
    polars.testing.assert_frame_equal(trimmed_dd.data, expected_df)


def test_trim_pre_and_post_drive_custom_threshold():
    # Create a sample Polars DataFrame with pre and post drive segments
    data = {
        "SimTime": [0, 1, 2, 3, 4, 5, 6, 7],
        "Velocity": [0.0, 0.5, 1.0, 3.0, 4.0, 0.8, 0.3, 0.0],
    }
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

    # Apply the filter with custom threshold
    trimmed_dd = trimPreAndPostDrive(dd, velocity_threshold=0.5)

    # Expected result (indexes 1-5 where velocity >= 0.5)
    expected_indices = [1, 2, 3, 4, 5]
    expected_df = df[expected_indices]
    polars.testing.assert_frame_equal(trimmed_dd.data, expected_df)


def test_trim_pre_and_post_drive_custom_column():
    # Create a sample Polars DataFrame with pre and post drive segments
    data = {
        "SimTime": [0, 1, 2, 3, 4, 5],
        "Speed": [0.0, 0.05, 0.2, 0.3, 0.05, 0.0],
    }
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

    # Apply the filter with custom column
    trimmed_dd = trimPreAndPostDrive(dd, velocity_col="Speed", velocity_threshold=0.1)

    # Expected result (indexes 2-3 where Speed > 0.1)
    expected_indices = [2, 3]
    expected_df = df[expected_indices]
    polars.testing.assert_frame_equal(trimmed_dd.data, expected_df)


def test_trim_pre_and_post_drive_no_trim_needed():
    # Create a sample Polars DataFrame where all data is above threshold
    data = {
        "SimTime": [0, 1, 2, 3, 4],
        "Velocity": [0.5, 0.6, 0.7, 0.8, 0.9],
    }
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

    # Apply the filter
    trimmed_dd = trimPreAndPostDrive(dd)

    # All data should be kept
    pl.testing.assert_frame_equal(trimmed_dd.data, df)


def test_trim_pre_and_post_drive_all_below_threshold():
    # Create a sample Polars DataFrame where all data is below threshold
    data = {
        "SimTime": [0, 1, 2, 3, 4],
        "Velocity": [0.0, 0.05, 0.05, 0.05, 0.0],
    }
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

    # Apply the filter
    trimmed_dd = trimPreAndPostDrive(dd)

    # Result should be empty
    assert trimmed_dd.data.is_empty()


def test_trim_pre_and_post_drive_missing_column():
    # Create a sample Polars DataFrame without required column
    data = {"SimTime": [0, 1, 2, 3, 4]}
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

    # This should raise an exception when the column check fails
    with pytest.raises(Exception):
        trimPreAndPostDrive(dd)


<<<<<<< HEAD
def test_sim_time_from_dat_time():
    data = {
        "DatTime": [10.0, 11.0, 12.0],
        "OtherCol": [1, 2, 3]
    }
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

    result = SimTimeFromDatTime(dd)

    expected_df = df.with_columns(pl.col("DatTime").alias("SimTime"))
    pl.testing.assert_frame_equal(result.data, expected_df)


def test_remove_data_outside():
    data = {
        "Speed": [5.0, 10.0, 15.0, 20.0],
        "OtherCol": [1, 2, 3, 4]
    }
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

    result = removeDataOutside(dd, col="Speed", lower=10.0, upper=15.0)

    # Only values outside [10, 15] will remain
    expected_df = df.filter(~((pl.col("Speed") >= 10.0) & (pl.col("Speed") <= 15.0)))
    pl.testing.assert_frame_equal(result.data, expected_df)


def test_number_binary_blocks_basic():
    data = {
        "SimTime": [0, 1, 2, 3, 4, 5],
        "ButtonStatus": [0, 0, 1, 1, 0, 1],
=======
def test_nullify_outlier_default_parameters():
    # Create a sample Polars DataFrame with outliers in HeadwayDistance
    data = {
        "SimTime": [0, 1, 2, 3, 4, 5],
        "HeadwayDistance": [500.0, 800.0, 1500.0, 2000.0, 950.0, 700.0],
>>>>>>> origin/R2DRV
    }
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

<<<<<<< HEAD
    result = numberBinaryBlocks(dd)

    expected = [0, 0, 1, 1, 2, 3]
    assert result.data["NumberedBlocks"].to_list() == expected


def test_number_binary_blocks_only_on():
    data = {
        "SimTime": [0, 1, 2, 3, 4],
        "ButtonStatus": [1, 1, 0, 1, 0],
=======
    # Apply the filter with default parameters (HeadwayDistance, threshold=1000)
    filtered_dd = nullifyOutlier(dd)

    # Expected result (values >1000 replaced with None)
    expected_df = pl.DataFrame({
        "SimTime": [0, 1, 2, 3, 4, 5],
        "HeadwayDistance": [500.0, 800.0, None, None, 950.0, 700.0],
    })

    pl.testing.assert_frame_equal(filtered_dd.data, expected_df)


def test_nullify_outlier_custom_threshold():
    # Create a sample Polars DataFrame with outliers
    data = {
        "SimTime": [0, 1, 2, 3, 4],
        "HeadwayDistance": [50.0, 150.0, 200.0, 500.0, 100.0],
>>>>>>> origin/R2DRV
    }
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

<<<<<<< HEAD
    result = numberBinaryBlocks(dd, only_on=1)

    # Only rows with ButtonStatus==1 remain, block numbers shifted and divided
    assert all(result.data["ButtonStatus"] == 1)
    assert result.data["NumberedBlocks"].to_list() == [1.0, 1.0, 2.0]


def test_jenks_basic_classification():
    data = {
        "SimTime": [0, 1, 2, 3, 4],
        "headPitch": [5.0, 5.2, 10.0, 10.2, 10.5],  # Two natural clusters
=======
    # Apply the filter with custom threshold
    filtered_dd = nullifyOutlier(dd, threshold=200)

    # Expected result (values >200 replaced with None)
    expected_df = pl.DataFrame({
        "SimTime": [0, 1, 2, 3, 4],
        "HeadwayDistance": [50.0, 150.0, 200.0, None, 100.0],
    })

    pl.testing.assert_frame_equal(filtered_dd.data, expected_df)


def test_nullify_outlier_custom_column():
    # Create a sample Polars DataFrame with outliers in a different column
    data = {
        "SimTime": [0, 1, 2, 3, 4],
        "Speed": [30.0, 120.0, 150.0, 200.0, 50.0],
>>>>>>> origin/R2DRV
    }
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

<<<<<<< HEAD
    result = Jenks(dd, oldCol="headPitch", newCol="hpBinary")

    # Check only 0 and 1 are present
    unique_vals = set(result.data["hpBinary"].to_list())
    assert unique_vals.issubset({0, 1})
    assert len(unique_vals) == 2


def test_fix_reversed_road_linear_land():
    data = {
        "SimTime": [0, 1, 2, 3, 4],
        "XPos": [600, 750, 800, 850, 950],
        "RoadOffset": [1.0, 2.0, -3.0, 4.0, -5.0],
=======
    # Apply the filter with custom column name
    filtered_dd = nullifyOutlier(dd, col="Speed", threshold=100)

    # Expected result (values >100 replaced with None)
    expected_df = pl.DataFrame({
        "SimTime": [0, 1, 2, 3, 4],
        "Speed": [30.0, None, None, None, 50.0],
    })

    pl.testing.assert_frame_equal(filtered_dd.data, expected_df)


def test_nullify_outlier_no_outliers():
    # Create a sample Polars DataFrame with no outliers
    data = {
        "SimTime": [0, 1, 2, 3, 4],
        "HeadwayDistance": [500.0, 600.0, 700.0, 800.0, 900.0],
>>>>>>> origin/R2DRV
    }
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

<<<<<<< HEAD
    result = FixReversedRoadLinearLand(dd)

    expected = [1.0, -2.0, 3.0, -4.0, -5.0]
    actual = result.data["RoadOffset"].to_list()
    assert actual == expected


def test_setinrange_basic():
    data = {
        "SimTime": [0, 1, 2, 3, 4],
        "Speed": [10, 15, 20, 25, 30],
        "Flag": [0, 0, 0, 0, 0],
    }
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

    # Set Flag to 1 where Speed is in range [15, 25]
    result = setinrange(dd, coltoset="Flag", valtoset=1, colforrange="Speed", rangemin=15, rangemax=25)

    expected = [0, 1, 1, 1, 0]
    actual = result.data["Flag"].to_list()
    assert actual == expected


def test_zscore_col():
    data = {
        "SimTime": [0, 1, 2, 3],
        "ReactionTime": [1.0, 2.0, 3.0, 4.0],
    }
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

    result = zscoreCol(dd, col="ReactionTime", newcol="zReactionTime")

    expected = [-1.1619, -0.3873, 0.3873, 1.1619]
    actual = result.data["zReactionTime"].to_list()

    np.testing.assert_allclose(actual, expected, rtol=1e-4)


def test_relative_box_pos():
    data = {
        "SimTime": [0, 1, 2, 3],
        "XPos": [100, 100, 100, 100],  # start_x = 100
        "BoxPosY": [110, 120, 130, 90],  # relative: 10, 20, 30, 0 (clipped)
    }
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

    result = relativeBoxPos(dd)
    expected = [10.0, 20.0, 30.0, 0.0]
    actual = result.data["relativeBoxStart"].to_list()

    assert actual == expected


def test_remove_data_outside():
    data = {
        "SimTime": [0, 1, 2, 3, 4],
        "Speed": [10.0, 20.0, 30.0, 40.0, 50.0],
    }
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

    # keep only values outside [20, 40]
    result = removeDataOutside(dd, col="Speed", lower=20.0, upper=40.0)

    expected = [10.0, 50.0]
    actual = result.data["Speed"].to_list()
    assert actual == expected


def test_separate_data_binary():
    data = {
        "SimTime": [0, 1, 2, 3, 4],
        "headPitch": [5, 10, 15, 20, 25],
    }
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

    result = separateData(dd, col="headPitch", threshold=15, high=1, low=0)

    expected = [0, 0, 1, 1, 1]
    actual = result.data["headPitch_categorized"].to_list()

    assert actual == expected


def test_write_to_csv(tmp_path):
    data = {
        "SimTime": [0, 1, 2],
        "Velocity": [0.1, 0.2, 0.3],
    }
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test_session.dat")

    output_dir = tmp_path / "out"
    output_dir.mkdir()
    result = writeToCSV(dd, str(output_dir))

    # Fix: determine correct expected file name from code logic
    expected_file = output_dir.parent / "test_session.csv"

    assert expected_file.exists()
    df_read = pl.read_csv(expected_file)
    pl.testing.assert_frame_equal(df_read, df)


def test_filetime_to_datetime():
    # Given FILETIME = 132199584000000000 corresponds to this time:
    expected = datetime.datetime(2019, 12, 4, 18, 40, tzinfo=datetime.timezone.utc)
    result = filetimeToDatetime(132199584000000000)

    assert result == expected


def test_merge_split_filetime():
    # 64-bit value split into two 32-bit integers
    full_value = 12345678901234567890
    low = full_value & 0xFFFFFFFF
    high = (full_value >> 32) & 0xFFFFFFFF

    merged = mergeSplitFiletime(high, low)
    assert merged == full_value


def test_remove_data_inside():
    data = {
        "SimTime": [0, 1, 2, 3, 4],
        "Speed": [5.0, 10.0, 15.0, 20.0, 25.0],
    }
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

    # Expect to remove rows where Speed ∈ [10, 20]
    result = removeDataInside(dd, col="Speed", lower=10.0, upper=20.0)

    expected_df = df.filter((pl.col("Speed") < 10.0) | (pl.col("Speed") > 20.0))
    pl.testing.assert_frame_equal(result.data, expected_df)


def test_filter_values_below():
    data = {
        "SimTime": [0, 1, 2, 3, 4],
        "Velocity": [0.5, 1.0, 2.0, 0.9, 1.5],
    }
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

    result = filterValuesBelow(dd, col="Velocity", threshold=1.0)

    expected_df = df.filter(pl.col("Velocity") >= 1.0)
    pl.testing.assert_frame_equal(result.data, expected_df)

=======
    # Apply the filter
    filtered_dd = nullifyOutlier(dd, threshold=1000)

    # No values should change
    pl.testing.assert_frame_equal(filtered_dd.data, df)


def test_nullify_outlier_missing_column():
    # Create a sample Polars DataFrame without the required column
    data = {"SimTime": [0, 1, 2, 3, 4]}
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

    # Apply the filter with default parameters
    filtered_dd = nullifyOutlier(dd)

    # Should return original data when column is missing (function handles exception)
    pl.testing.assert_frame_equal(filtered_dd.data, df)


def test_nullify_outlier_all_outliers():
    # Create a sample Polars DataFrame where all values are outliers
    data = {
        "SimTime": [0, 1, 2, 3],
        "HeadwayDistance": [1500.0, 2000.0, 3000.0, 5000.0],
    }
    df = pl.DataFrame(data, schema= [
        ("SimTime",  pl.datatypes.Float32),
        ("HeadwayDistance", pl.datatypes.Float32)
    ])
    dd = pydre.core.DriveData.init_test(df, "test.dat")

    # Apply the filter
    filtered_dd = nullifyOutlier(dd, threshold=1000)

    # All values in HeadwayDistance should be None
    expected_df = pl.DataFrame({
        "SimTime": [0, 1, 2, 3],
        "HeadwayDistance": [None, None, None, None],
    }, schema= [
        ("SimTime",  pl.datatypes.Float32),
        ("HeadwayDistance", pl.datatypes.Float32)
    ])

    pl.testing.assert_frame_equal(filtered_dd.data, expected_df)
>>>>>>> origin/R2DRV
