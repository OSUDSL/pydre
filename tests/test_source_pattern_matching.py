from pydre.project import Project
from pathlib import Path


def test_not_supported_source(tmp_path, caplog, capsys):
    toml = tmp_path / "no_pattern.toml"
    toml.write_text("""
        [config]
        source = "pppp"  
    """)

    # Capture ERROR logs
    caplog.set_level("ERROR")
    # Initialize project
    project = Project(str(toml))
    # Reads and returns captured output so far
    out, err = capsys.readouterr()
    # Assert that the specific error message was logged
    assert ("Source specified in project definition not supported" in caplog.text or 
            "Source specified in project definition not supported" in err)


def test_pattern_matching(tmp_path):
    # Create a temporary directory 
    tmp_dir = tmp_path / "test_dir"
    tmp_dir.mkdir()

    # Create a temporary empty test data file that matches the pattern
    tmp_test_data_file = tmp_dir / "Experimenter_43_Control_1752683477.dat"
    tmp_test_data_file.touch()

    toml = tmp_dir / "pattern_matching.toml"
    toml.write_text(f"""
        [config]
        source = "localfilesystem"
        baseDirectory = "{tmp_dir.as_posix()}"
        pattern = "_Control_1752683477"
    """)

    # Initialize project
    project = Project(str(toml))

    expected_path = Path(tmp_test_data_file)

    # Assert project.local_data_files contains the correct matched path
    assert  expected_path in (Path(f) for f in project.local_data_files)


def test_pattern_matching_with_datafiles(tmp_path):
    # Create a temporary directory
    tmp_dir = tmp_path / "test_dir"
    tmp_dir.mkdir()

    # Create temporary empty test data files that match the pattern and are explicitly specified in the .toml file
    file_names = ["Experimenter_38_Test A_1750181710.dat", "Experimenter_4_Control_1734190953.dat", 
                   "Experimenter_4_Test B_1734190306.dat", "Experimenter_4_Practice_1734189807.dat"]
    for name in file_names:
        (tmp_dir / name).touch()

    explicit_file = (tmp_dir / "Experimenter_38_Test A_1750181710.dat").as_posix()

    toml = tmp_dir / "pattern_matching_and_datafiles.toml"
    toml.write_text(f"""
        [config]
        source = "localfilesystem"
        baseDirectory = "{tmp_dir.as_posix()}"
        pattern = "_4_"
        datafiles = ["{explicit_file}"]
    """)

    # Initialize project
    project = Project(str(toml))

    expected_paths = {tmp_dir / name for name in file_names}

    # Assert project.local_data_files contains the correct matched path
    assert expected_paths.issubset({Path(f) for f in project.local_data_files})


def test_datafiles_no_source(tmp_path, caplog, capsys):
    # Create a temporary directory
    tmp_dir = tmp_path / "test_dir"
    tmp_dir.mkdir()

    # Create a temporary empty test data file that is explicitly specified in the .toml file
    tmp_test_data_file = (tmp_dir / "Experimenter_43_Control_1752683477.dat")
    tmp_test_data_file.touch()
        
    toml = tmp_dir / "datafiles_no_source.toml"
    toml.write_text(f"""
        [config]
        datafiles = ["{tmp_test_data_file.as_posix()}"]
    """)

    # Capture WARNING logs
    caplog.set_level("WARNING")

    # Intializes a project
    project = Project(str(toml))

    # Reads and returns captured output so far
    out, err = capsys.readouterr()

    # Assert that the specific error message was logged
    assert ("No source specified in project definition, setting source as local file system" in caplog.text or "No source specified in project definition, setting source as local file system" in err)


def test_no_base_directory(tmp_path, caplog, capsys):
    toml = tmp_path / "datafiles_no_source.toml"
    toml.write_text("""
        [config]
        source = "localfilesystem"
        pattern = "_4_"
    """)

    # Capture ERROR logs
    caplog.set_level("ERROR")

    # Intializes a project
    project = Project(str(toml))

    # Reads and returns captured output so far
    out, err = capsys.readouterr()

    # Assert that the specific error message was logged
    assert ("No baseDirectory found in project definition" in caplog.text or "No baseDirectory found in project definition" in err)


def test_just_pattern(tmp_path, caplog, capsys):
    toml = tmp_path / "just_pattern.toml"
    toml.write_text("""
        [config]
        pattern = "_4_"
    """)

    # Capture ERROR logs
    caplog.set_level("ERROR")

    # Intializes a project
    project = Project(str(toml))

    # Reads and returns captured output so far
    out, err = capsys.readouterr()

    # Assert that the specific error message was logged
    assert ("No source specified in project definition" in caplog.text or "No source specified in project definition" in err)


def test_additionalFiles_patternMatching_and_datafiles(tmp_path):
    # Create a temporary directory
    tmp_dir = tmp_path / "test_dir"
    tmp_dir.mkdir()

    # Create temporary empty test data files that match the pattern, explicitly specified in the .toml file, 
    # and additional file paths specified through the command line
    file_names = ["Experimenter_24_Test A_1739299126.dat", "Experimenter_38_Test A_1750181710.dat", 
                    "Experimenter_4_Control_1734190953.dat", 
                    "Experimenter_4_Test B_1734190306.dat",
                    "Experimenter_4_Practice_1734189807.dat"]
    for name in file_names:
        (tmp_dir / name).touch()

    explicit_file = (tmp_dir / "Experimenter_38_Test A_1750181710.dat").as_posix()

    toml = tmp_dir / "patternMatching_and_datafiles.toml"
    toml.write_text(f"""
        [config]
        source = "localfilesystem"
        baseDirectory = "{tmp_dir.as_posix()}"
        pattern = "_4_"
        datafiles = ["{explicit_file}"]
    """)

    additional_paths = [f"{tmp_dir.as_posix()}/Experimenter_24_Test A_1739299126.dat"]

    # Intializes a project
    project = Project(str(toml), additional_paths)

    expected_paths = {tmp_dir / name for name in file_names}
    
    # Assert project.local_data_files contains the correct matched path, file paths explicitly specified in the .toml file, 
    # and additional file paths specified through the command line.
    assert expected_paths.issubset({Path(f) for f in project.local_data_files})

    


