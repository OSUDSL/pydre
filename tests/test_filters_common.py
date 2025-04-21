import polars as pl
import pytest
import pydre.core
import polars.testing

from pydre.filters.common import trimPreAndPostDrive


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

