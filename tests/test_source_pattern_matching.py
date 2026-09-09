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
    assert ("Source specified in project definition not supported" in caplog.text or "Source specified in project definition not supported" in err)


def test_pattern_matching(tmp_path):
    toml = tmp_path / "pattern_matching.toml"
    toml.write_text("""
        [config]
        source = "localfilesystem"
        baseDirectory = "C:/Users/jandj/Desktop/drive_da_files"
        pattern = "_Control_1752683477"
    """)
    # Initialize project
    project = Project(str(toml))

    expected_path = Path("C:/Users/jandj/Desktop/drive_da_files/Experimenter_43_Control_1752683477.dat")

    # Assert project.local_data_files contains the correct matched path
    assert  expected_path in (Path(f) for f in project.local_data_files)


def test_pattern_matching_with_datafiles(tmp_path):
    toml = tmp_path / "pattern_matching_and_datafiles.toml"
    toml.write_text("""
        [config]
        source = "localfilesystem"
        baseDirectory = "C:/Users/jandj/Desktop/drive_da_files"
        pattern = "_4_"
        datafiles = ["C:/Users/jandj/Desktop/drive_da_files/Experimenter_38_Test A_1750181710.dat"]
    """)
    # Initialize project
    project = Project(str(toml))

    expected_paths = {Path("C:/Users/jandj/Desktop/drive_da_files/Experimenter_38_Test A_1750181710.dat"),
            Path("C:/Users/jandj/Desktop/drive_da_files/Experimenter_4_Control_1734190953.dat"),
            Path("C:/Users/jandj/Desktop/drive_da_files/Experimenter_4_Test B_1734190306.dat"),
            Path("C:/Users/jandj/Desktop/drive_da_files/Experimenter_4_Practice_1734189807.dat")}

    # Assert project.local_data_files contains the correct matched path
    assert expected_paths.issubset({Path(f) for f in project.local_data_files})


def test_datafiles_no_source(tmp_path, caplog, capsys):
    toml = tmp_path / "datafiles_no_source.toml"
    toml.write_text("""
        [config]
        datafiles = ["C:/Users/jandj/Desktop/drive_da_files/Experimenter_43_Control_1752683477.dat", 
        "C:/Users/jandj/Desktop/drive_da_files/Experimenter_41_Practice_1752601959.dat", 
        "C:/Users/jandj/Desktop/drive_da_files/Experimenter_41_Accommodation Drive_1752601503.dat"]
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


def test_additionalFiles_patternMatching_and_datafiles(tmp_path, caplog, capsys):
    toml = tmp_path / "patternMatching_and_datafiles.toml"
    toml.write_text("""
        [config]
        source = "localfilesystem"
        baseDirectory = "C:/Users/jandj/Desktop/drive_da_files"
        pattern = "_4_"
        datafiles = ["C:/Users/jandj/Desktop/drive_da_files/Experimenter_38_Test A_1750181710.dat"]
    """)

    additional_paths = ["C:/Users/jandj/Desktop/drive_da_files/Experimenter_24_Test A_1739299126.dat"]

    # Intializes a project
    project = Project(str(toml), additional_paths)

    expected_paths = {Path("C:/Users/jandj/Desktop/drive_da_files/Experimenter_24_Test A_1739299126.dat"),
                Path("C:/Users/jandj/Desktop/drive_da_files/Experimenter_38_Test A_1750181710.dat"),
                Path("C:/Users/jandj/Desktop/drive_da_files/Experimenter_4_Control_1734190953.dat"),
                Path("C:/Users/jandj/Desktop/drive_da_files/Experimenter_4_Test B_1734190306.dat"),
                Path("C:/Users/jandj/Desktop/drive_da_files/Experimenter_4_Practice_1734189807.dat")}
    
    # Assert project.local_data_files contains the correct matched path, file paths explicitly specified in the .toml file, 
    # and additional file paths specified through the command line.
    assert expected_paths.issubset({Path(f) for f in project.local_data_files})

    


