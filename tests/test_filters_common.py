import polars as pl
import polars.datatypes
import pytest
import pydre.core
import polars.testing

from pydre.filters.common import trimPreAndPostDrive
from pydre.filters.common import nullifyOutlier



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


def test_nullify_outlier_default_parameters():
    # Create a sample Polars DataFrame with outliers in HeadwayDistance
    data = {
        "SimTime": [0, 1, 2, 3, 4, 5],
        "HeadwayDistance": [500.0, 800.0, 1500.0, 2000.0, 950.0, 700.0],
    }
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

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
    }
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

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
    }
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

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
    }
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

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