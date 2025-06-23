from pathlib import Path
import pytest
import pydre.project
import polars as pl
import polars.testing
import tomllib

from pydre.core import DriveData
from loguru import logger

FIXTURE_DIR = Path(__file__).parent.resolve() / "test_data"


@pytest.mark.datafiles(FIXTURE_DIR / "good_projectfiles" / "test1_pf.json")
def test_project_loadjson(datafiles):
    proj = pydre.project.Project(datafiles / "test1_pf.json")
    assert isinstance(proj, pydre.project.Project)


@pytest.mark.datafiles(FIXTURE_DIR / "good_projectfiles" / "test1_pf.toml")
def test_project_loadtoml(datafiles):
    proj = pydre.project.Project(datafiles / "test1_pf.toml")
    assert isinstance(proj, pydre.project.Project)


def test_project_loadbadtoml():
    with pytest.raises(FileNotFoundError):
        proj = pydre.project.Project("doesnotexist.toml")


@pytest.mark.datafiles(
    FIXTURE_DIR / "good_projectfiles" / "test1_pf.json",
    FIXTURE_DIR / "good_projectfiles" / "test1_pf.toml",
)
def test_project_projequiv(datafiles):
    proj_json = pydre.project.Project(datafiles / "test1_pf.json")
    proj_toml = pydre.project.Project(datafiles / "test1_pf.toml")
    assert proj_json == proj_toml


@pytest.mark.datafiles(
    FIXTURE_DIR / "good_projectfiles",
    FIXTURE_DIR / "test_custom_metric",
    FIXTURE_DIR / "test_datfiles",
    keep_top_dir=True,
)
def test_project_custom_metric(datafiles):
    resolved_data_file = str(
        datafiles / "test_datfiles" / "clvspectest_Sub_8_Drive_3.dat"
    )
    proj = pydre.project.Project(
        datafiles / "good_projectfiles" / "custom_test.toml",
        additional_data_paths=[resolved_data_file],
    )
    proj.processDatafiles(numThreads=2)

    expected_result = pl.DataFrame(
        [
            {
                "ParticipantID": "8",
                "UniqueID": "3",
                "ScenarioName": "Drive",
                "DXmode": "Sub",
                "ROI": None,
                "custom_test": 1387.6228702430055,
            }
        ]
    )

    polars.testing.assert_frame_equal(proj.results, expected_result)


def test_project_bad_toml_format(tmp_path):
    bad_toml = tmp_path / "bad.toml"
    bad_toml.write_text("bad:::toml")

    project = pydre.project.Project(bad_toml)
    assert project.definition == {} or project.definition is None


def test_project_missing_keys_toml(tmp_path):
    toml = tmp_path / "empty.toml"
    toml.write_text('title = "Empty project"')  # no rois, metrics, filters

    project = pydre.project.Project(toml)
    assert project.definition == {}  # no keys restructured


def test_project_additional_data_paths(tmp_path):
    test_file = tmp_path / "data1.dat"
    test_file.write_text("VidTime SimTime\n1 1\n2 2")

    dummy_toml = tmp_path / "base.toml"
    dummy_toml.write_text("""
        [config]
        datafiles = []
    """)

    project = pydre.project.Project(dummy_toml, additional_data_paths=[str(test_file)])
    assert str(test_file) in project.config["datafiles"]


def test_process_filter_missing_function():
    dummy_data = DriveData()
    bad_filter = {"name": "invalidfilter"}
    with pytest.raises(KeyError):
        pydre.project.Project.processFilter(bad_filter, dummy_data)


def test_process_roi_unknown_type():
    dummy_data = DriveData()
    unknown_roi = {"type": "nonexistent", "filename": "roi.csv"}
    result = pydre.project.Project.processROI(unknown_roi, dummy_data)
    assert result == [dummy_data]


def test_save_results_without_running(tmp_path):
    dummy_toml = tmp_path / "dummy.toml"
    dummy_toml.write_text("""
        [config]
        datafiles = []
    """)
    project = pydre.project.Project(dummy_toml)
    project.results = None
    project.config["outputfile"] = str(tmp_path / "out.csv")

    # Should not raise error, just log it
    project.saveResults()
    assert not (tmp_path / "out.csv").exists()


def test_project_toml_full_definition(tmp_path):
    toml = tmp_path / "full.toml"
    toml.write_text("""
    [rois.rect1]
    type = "rect"
    filename = "roi.csv"

    [metrics.metric1]
    name = "m1"
    function = "test_metric"

    [filters.filter1]
    name = "f1"
    function = "test_filter"

    [config]
    datafiles = []
    """)

    project = pydre.project.Project(toml)
    assert isinstance(project.definition.get("rois"), list)
    assert isinstance(project.definition.get("metrics"), list)
    assert isinstance(project.definition.get("filters"), list)
    assert isinstance(project.config, dict)


def test_project_toml_with_extra_keys(tmp_path):
    toml = tmp_path / "weird.toml"
    toml.write_text("""
    title = "strange"
    [config]
    datafiles = []
    """)

    project = pydre.project.Project(toml)
    assert project.definition == {}


def test_project_outputfile_override(tmp_path):
    toml = tmp_path / "config.toml"
    toml.write_text("""
    [config]
    datafiles = []
    outputfile = "default.csv"
    """)

    override_file = tmp_path / "override.csv"
    project = pydre.project.Project(toml, outputfile=str(override_file))
    assert project.config["outputfile"] == str(override_file)


def test_project_ignore_files(tmp_path):
    data_file = tmp_path / "real.dat"
    data_file.write_text("VidTime SimTime\n1 1")
    ignored_file = tmp_path / "ignore_this.dat"
    ignored_file.write_text("VidTime SimTime\n1 1")

    toml = tmp_path / "ignore.toml"
    toml.write_text(f"""
    [config]
    datafiles = ["*.dat"]
    ignore = ["ignore_this"]
    """)

    project = pydre.project.Project(toml)
    assert all("ignore_this" not in str(f) for f in project.filelist)
    assert any("real" in str(f) for f in project.filelist)


def test_process_metric_missing_fields():
    dummy_data = DriveData()
    metric = {"function": "nonexistent_func"}
    project = pydre.project.Project.__new__(pydre.project.Project)
    with pytest.raises(KeyError):
        project.processMetric(metric, dummy_data)

