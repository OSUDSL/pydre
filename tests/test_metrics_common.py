import pydre.core
import polars as pl
import pytest
import pydre.metrics
import pydre.metrics.common


def test_colMean():
    # Create a sample Polars DataFrame

    data = {"A": [1, 2, 3, 4, 5], "B": [10, 20, 30, 40, 50]}
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

    # Test cases
    assert pydre.metrics.common.colMean(dd, var="A") == 3.0
    assert pydre.metrics.common.colMean(dd, var="B") == 30.0

    # Test cases with cutoff
    assert pydre.metrics.common.colMean(dd, var="A", cutoff=2.5) == 4.0
    assert pydre.metrics.common.colMean(dd, var="B", cutoff=25) == 40.0

    # Test for an invalid column name
    assert pydre.metrics.common.colMean(dd, var="InvalidColumn") is None


def test_colMedian():
    # Create a sample Polars DataFrame
    data = {"A": [-1, 2, 3, 4, 5], "B": [-10, 20, 30, 40, 50]}
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

    # Test cases
    assert pydre.metrics.common.colMedian(dd, var="A") == 3.0
    assert pydre.metrics.common.colMedian(dd, var="B") == 30.0

    assert pydre.metrics.common.colMedian(dd, var="A", cutoff=2.5) == 4.0
    assert pydre.metrics.common.colMedian(dd, var="B", cutoff=25) == 40.0

    # Test for an invalid column name
    assert pydre.metrics.common.colMedian(dd, var="InvalidColumn") is None


def test_colSD():
    # Create a sample Polars DataFrame
    data = {"A": [1, 2, 3, 4, 5], "B": [10, 20, 30, 40, 50]}
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

    # Test cases
    assert pytest.approx(pydre.metrics.common.colSD(dd, var="A"), 0.01) == 1.58
    assert pytest.approx(pydre.metrics.common.colSD(dd, var="B"), 0.01) == 15.8

    # Test for an invalid column name
    assert pydre.metrics.common.colSD(dd, var="InvalidColumn") is None


def test_colMax():
    # Create a sample Polars DataFrame
    data = {"A": [1, 2, 3, 4, 5], "B": [10, 20, 30, 40, 50]}
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

    # Test cases
    assert pydre.metrics.common.colMax(dd, var="A") == 5
    assert pydre.metrics.common.colMax(dd, var="B") == 50

    # Test for an invalid column name
    assert pydre.metrics.common.colMax(dd, var="InvalidColumn") is None


def test_colMin():
    # Create a sample Polars DataFrame
    data = {"A": [1, 2, 3, 4, 5], "B": [10, 20, 30, 40, 50]}
    df = pl.DataFrame(data)
    dd = pydre.core.DriveData.init_test(df, "test.dat")

    # Test cases
    assert pydre.metrics.common.colMin(dd, var="A") == 1
    assert pydre.metrics.common.colMin(dd, var="B") == 10

    # Test for an invalid column name
    assert pydre.metrics.common.colMin(dd, var="InvalidColumn") is None


def test_timeAboveSpeed():
    # Create sample Polars DataFrames for testing
    data1 = {"SimTime": [0, 1, 2, 3, 4], "Velocity": [10, 20, 30, 40, 50]}
    df1 = pl.DataFrame(data1)
    dd1 = pydre.core.DriveData.init_test(df1, "test1.dat")

    data2 = {"SimTime": [0, 1, 2, 3], "Velocity": [5, 15, 25, 35]}  # Shorter duration
    df2 = pl.DataFrame(data2)
    dd2 = pydre.core.DriveData.init_test(df2, "test2.dat")

    # Test cases with various cutoffs and percentage options
    assert pydre.metrics.common.timeAboveSpeed(dd1) == 4
    assert (
        pydre.metrics.common.timeAboveSpeed(dd1, cutoff=30) == 3
    )  # 3 seconds above 30
    assert (
        pydre.metrics.common.timeAboveSpeed(dd1, cutoff=30.1) == 2
    )  # 2 seconds above 30.1
    assert pydre.metrics.common.timeAboveSpeed(dd1, cutoff=25, percentage=True) == (
        3 / 4
    )
    assert pydre.metrics.common.timeAboveSpeed(dd2, cutoff=20) == 2
    assert pydre.metrics.common.timeAboveSpeed(dd2, cutoff=40) == 0  # No time above 40

    # Test with a cutoff that results in no time above
    assert pydre.metrics.common.timeAboveSpeed(dd1, cutoff=60) == 0

    # Test with missing required columns
    data3 = {"SimTime": [0, 1, 2], "OtherColumn": [1, 2, 3]}
    df3 = pl.DataFrame(data3)
    dd3 = pydre.core.DriveData.init_test(df3, "test3.dat")
    assert pydre.metrics.common.timeAboveSpeed(dd3) is None

    # Test with non-numeric columns (assuming it raises ColumnsMatchError)
    data4 = {"SimTime": [0, 1, 2], "Velocity": ["slow", "medium", "fast"]}
    df4 = pl.DataFrame(data4)
    dd4 = pydre.core.DriveData.init_test(df4, "test4.dat")
    assert pydre.metrics.common.timeAboveSpeed(dd4) is None


def test_timeWithinSpeedLimit():
    # Create sample Polars DataFrames for testing
    data1 = {
        "SimTime": [0, 1, 2, 3, 4],
        "Velocity": [10, 12, 18, 20, 25],  # in meters per second
        "SpeedLimit": [35, 35, 35, 50, 50],  # in miles per hour
    }
    df1 = pl.DataFrame(data1)
    dd1 = pydre.core.DriveData.init_test(df1, "test1.dat")

    data2 = {"SimTime": [0, 1, 2], "Velocity": [5, 5, 25], "SpeedLimit": [30, 30, 60]}
    df2 = pl.DataFrame(data2)
    dd2 = pydre.core.DriveData.init_test(df2, "test2.dat")

    # Test cases with various lower limits and percentage options
    assert pydre.metrics.common.timeWithinSpeedLimit(dd1, lowerlimit=0) == 2
    assert (
        pydre.metrics.common.timeWithinSpeedLimit(dd1, lowerlimit=20, percentage=True)
        == 0.5
    )
    assert pydre.metrics.common.timeWithinSpeedLimit(dd2, lowerlimit=10) == 2
    assert pydre.metrics.common.timeWithinSpeedLimit(dd2, lowerlimit=20) == 1

    # Test with a lower limit that results in no time within limit
    assert pydre.metrics.common.timeWithinSpeedLimit(dd1, lowerlimit=100) == 0

    # Test with missing required columns
    data3 = {"SimTime": [0, 1, 2], "Velocity": [10, 20, 30]}
    df3 = pl.DataFrame(data3)
    dd3 = pydre.core.DriveData.init_test(df3, "test3.dat")
    assert pydre.metrics.common.timeWithinSpeedLimit(dd3) is None

    # Test with non-numeric columns
    data4 = {
        "SimTime": [0, 1, 2],
        "Velocity": ["slow", "medium", "fast"],
        "SpeedLimit": [30, 30, 40],
    }
    df4 = pl.DataFrame(data4)
    dd4 = pydre.core.DriveData.init_test(df4, "test4.dat")
    assert pydre.metrics.common.timeWithinSpeedLimit(dd4) is None

