import pytest
import os
from pathlib import Path
import argparse

from pydre.run import (
    parse_arguments, run_project, main,
    print_metrics, print_filters, _load_custom_from_project,
    _VERSION,
)

FIXTURE_DIR = Path(__file__).parent.resolve() / "test_data"
EXAMPLES_DIR = Path(__file__).parent.parent.resolve() / "examples"
CUSTOM_PROJECT_TOML = EXAMPLES_DIR / "custom_project" / "custom_test.toml"


# Fixtures for common mocks
@pytest.fixture
def mock_project(mocker):
    """Mock Project class and instance"""
    mock_project_class = mocker.patch("pydre.project.Project")
    mock_instance = mocker.MagicMock()
    mock_project_class.return_value = mock_instance
    return mock_project_class, mock_instance


@pytest.fixture
def mock_logger(mocker):
    """Mock logger functions"""
    return {
        "remove": mocker.patch("loguru.logger.remove"),
        "add": mocker.patch("loguru.logger.add"),
        "warning": mocker.patch("loguru.logger.warning"),
        "error": mocker.patch("loguru.logger.error"),
    }


def test_parse_arguments_version(capsys):
    """--version should print the version string and exit."""
    with pytest.raises(SystemExit) as exc_info:
        parse_arguments(["--version"])
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "pydre" in captured.out
    assert _VERSION in captured.out


def test_parse_arguments_minimal():
    """Test argument parsing with only required arguments."""
    args = parse_arguments(["-p", "project.toml"])
    assert args.projectfile == "project.toml"
    assert args.datafiles is None
    assert args.outputfile == "out.csv"
    assert args.warninglevel == "WARNING"
    assert args.list_metrics is False
    assert args.list_filters is False


def test_parse_arguments_full():
    """Test argument parsing with all arguments provided."""
    args = parse_arguments(
        [
            "-p",
            "project.toml",
            "-d",
            "file1.dat",
            "file2.dat",
            "-o",
            "output.csv",
            "-l",
            "DEBUG",
        ]
    )
    assert args.projectfile == "project.toml"
    assert args.datafiles == ["file1.dat", "file2.dat"]
    assert args.outputfile == "output.csv"
    assert args.warninglevel == "DEBUG"


def test_parse_arguments_log_level_long_form():
    """Test that --log-level is accepted as an alias for -l/--warninglevel."""
    args = parse_arguments(["--log-level", "DEBUG"])
    assert args.warninglevel == "DEBUG"


def test_parse_arguments_no_projectfile_defaults_to_none():
    """projectfile is now optional; omitting it should default to None (not raise SystemExit)."""
    args = parse_arguments([])
    assert args.projectfile is None


def test_parse_arguments_list_metrics_flag():
    """Test that --list-metrics flag is parsed correctly."""
    args = parse_arguments(["--list-metrics"])
    assert args.list_metrics is True
    assert args.projectfile is None


def test_parse_arguments_list_filters_flag():
    """Test that --list-filters flag is parsed correctly."""
    args = parse_arguments(["--list-filters"])
    assert args.list_filters is True
    assert args.projectfile is None



def test_run_project_basic(mock_project):
    """Test basic project run functionality."""
    mock_project_class, mock_instance = mock_project

    result = run_project("project.toml", ["data.dat"], "output.csv")

    mock_project_class.assert_called_once_with(
        "project.toml", ["data.dat"], "output.csv", log_level="WARNING"
    )
    expected_threads = max(1, int((os.cpu_count() or 1) * 0.75))

    mock_instance.processDatafiles.assert_called_once_with(
        numThreads=expected_threads
    )
    mock_instance.saveResults.assert_called_once()
    assert result == mock_instance


def test_run_project_custom_threads(mock_project):
    """Test project run with custom thread count."""
    mock_project_class, mock_instance = mock_project

    run_project("project.toml", ["data.dat"], "output.csv", num_threads=4)

    mock_instance.processDatafiles.assert_called_once_with(numThreads=4)


def test_run_project_missing_file(mocker):
    """Test project run with missing file."""
    mocker.patch(
        "pydre.project.Project", side_effect=FileNotFoundError("File not found")
    )

    with pytest.raises(FileNotFoundError):
        run_project("nonexistent.toml", ["data.dat"], "output.csv")


def test_main_success(mocker):
    """Test successful execution of main function."""
    mock_parse_args = mocker.patch("pydre.run.parse_arguments")
    mock_run_project = mocker.patch("pydre.run.run_project")

    mock_parse_args.return_value = argparse.Namespace(
        projectfile="project.toml",
        datafiles=["data.dat"],
        outputfile="output.csv",
        warninglevel="INFO",
        list_metrics=False,
        list_filters=False,
    )

    result = main(["dummy"])

    mock_parse_args.assert_called_once_with(["dummy"])
    mock_run_project.assert_called_once_with(
        "project.toml", ["data.dat"], "output.csv", log_level="INFO"
    )
    assert result == 0


def test_main_project_error(mocker, mock_logger):
    """Test main function with project processing error."""
    mock_parse_args = mocker.patch("pydre.run.parse_arguments")
    mocker.patch(
        "pydre.run.run_project", side_effect=FileNotFoundError("File not found")
    )

    mock_parse_args.return_value = argparse.Namespace(
        projectfile="project.toml",
        datafiles=["data.dat"],
        outputfile="output.csv",
        warninglevel="INFO",
        list_metrics=False,
        list_filters=False,
    )

    result = main([])

    assert result == 1
    mock_logger["error"].assert_called_once()
    assert "File not found" in mock_logger["error"].call_args[0][0]


def test_main_no_projectfile_returns_error(capsys):
    """main() without --projectfile and without a listing flag should return 1."""
    result = main([])
    assert result == 1
    captured = capsys.readouterr()
    assert "-p/--projectfile" in captured.out


def test_main_list_metrics(mocker):
    """--list-metrics should call print_metrics(None) and return 0 without a project file."""
    mock_print = mocker.patch("pydre.run.print_metrics")
    result = main(["--list-metrics"])
    assert result == 0
    mock_print.assert_called_once_with(None)


def test_main_list_metrics_with_project(mocker):
    """--list-metrics -p <file> should forward the project file to print_metrics."""
    mock_print = mocker.patch("pydre.run.print_metrics")
    result = main(["--list-metrics", "-p", "myproject.toml"])
    assert result == 0
    mock_print.assert_called_once_with("myproject.toml")


def test_main_list_filters(mocker):
    """--list-filters should call print_filters(None) and return 0 without a project file."""
    mock_print = mocker.patch("pydre.run.print_filters")
    result = main(["--list-filters"])
    assert result == 0
    mock_print.assert_called_once_with(None)


def test_main_list_filters_with_project(mocker):
    """--list-filters -p <file> should forward the project file to print_filters."""
    mock_print = mocker.patch("pydre.run.print_filters")
    result = main(["--list-filters", "-p", "myproject.toml"])
    assert result == 0
    mock_print.assert_called_once_with("myproject.toml")


def test_print_metrics_output(capsys):
    """print_metrics() should output at least the header and one known metric."""
    print_metrics()
    captured = capsys.readouterr()
    assert "METRIC NAME" in captured.out
    assert "colMean" in captured.out


def test_print_filters_output(capsys):
    """print_filters() should output at least the header and one known filter."""
    print_filters()
    captured = capsys.readouterr()
    assert "FILTER NAME" in captured.out
    assert "numberBinaryBlocks" in captured.out


# ---------------------------------------------------------------------------
# Custom metric/filter loading tests
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    not CUSTOM_PROJECT_TOML.exists(),
    reason="example custom project not present",
)
def test_print_metrics_includes_custom_metric(capsys):
    """print_metrics(-p custom_test.toml) should include the 'testMean' custom metric."""
    print_metrics(str(CUSTOM_PROJECT_TOML))
    captured = capsys.readouterr()
    assert "testMean" in captured.out


@pytest.mark.skipif(
    not CUSTOM_PROJECT_TOML.exists(),
    reason="example custom project not present",
)
def test_load_custom_from_project_registers_metric():
    """_load_custom_from_project should register 'testMean' into metricsList."""
    from pydre import metrics as m
    # testMean may already be registered from a previous test; ensure it's present after loading
    _load_custom_from_project(str(CUSTOM_PROJECT_TOML))
    assert "testMean" in m.metricsList


def test_load_custom_from_project_missing_file(capsys):
    """_load_custom_from_project with a non-existent path should print a warning, not raise."""
    _load_custom_from_project("nonexistent_project.toml")
    captured = capsys.readouterr()
    assert "[warning]" in captured.out
    assert "not found" in captured.out


def test_load_custom_from_project_bad_toml(tmp_path, capsys):
    """_load_custom_from_project with invalid TOML should print a warning, not raise."""
    bad_toml = tmp_path / "bad.toml"
    bad_toml.write_text("this is not [ valid toml !!!", encoding="utf-8")
    _load_custom_from_project(str(bad_toml))
    captured = capsys.readouterr()
    assert "[warning]" in captured.out


def test_load_custom_from_project_missing_custom_dir(tmp_path):
    """_load_custom_from_project with a custom dir that doesn't exist should warn gracefully, not raise."""
    toml_content = '[config]\ncustom_metrics_dirs = ["does_not_exist"]\n'
    pf = tmp_path / "test.toml"
    pf.write_text(toml_content, encoding="utf-8")
    # Should complete without raising even though the directory doesn't exist.
    # The warning is emitted via logger.warning() to stderr.
    _load_custom_from_project(str(pf))
