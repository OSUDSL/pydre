import unittest
import pydre.merge_tool as p_merge
import shutil
import os
import glob
import pandas as pd


class WritableObject:
    def __init__(self):
        self.content = []

    def write(self, string):
        self.content.append(string)


class TestMergeTool(unittest.TestCase):

    def setUp(self):
        # self.whatever to access them in the rest of the script, runs before other scripts
        self.merge_dirs = ["ref_dir", "ref_dir_spatial", "three_subs_seq", "seq_times", "one_file", "no_file",
                           "three_subs_spa", "standard_spa", "one_file_spa", "no_file_spa"]

    def tearDown(self):
        pass
        # runs after all test cases, threw this in here just in case

    # ----- Test Cases -----
    def test_reftest(self):
        # ---- MergeTool() Arguments ----
        index_of_dir = 0
        mergetype = "sequential"
        # -------------------------------
        self.template(index_of_dir, mergetype)

    def test_reftest_spatial(self):
        # ---- MergeTool() Arguments ----
        index_of_dir = 1
        mergetype = "spatial"
        # -------------------------------
        self.template(index_of_dir, mergetype)

    # Standard case of three subs w/ 3 drives, similar times. Sequential Merge.
    def test_sequential_standard1(self):
        # ---- MergeTool() Arguments ----
        index_of_dir = 2
        mergetype = "sequential"
        # -------------------------------
        self.template(index_of_dir, mergetype)

    # Standard case of one sub w/ 4 drives, very different times. Sequential Merge.
    def test_sequential_standard2(self):
        # ---- MergeTool() Arguments ----
        index_of_dir = 3
        mergetype = "sequential"
        # -------------------------------
        self.template(index_of_dir, mergetype)

    # Edge case in which the target directory only has one file.
    def test_sequential_one_file(self):
        # ---- MergeTool() Arguments ----
        index_of_dir = 4
        mergetype = "sequential"
        # -------------------------------
        self.template(index_of_dir, mergetype)

    # Edge case in which the target directory has no files. Expect program to warn the user, but not crash.
    def test_sequential_no_files(self):
        # ---- MergeTool() Arguments ----
        index_of_dir = 5
        mergetype = "sequential"
        # -------------------------------
        self.template(index_of_dir, mergetype)

    # Standard case of three subs w/ 3 drives, sensible locations. Spatial Merge.
    def test_spatial_standard1(self):
        # ---- MergeTool() Arguments ----
        index_of_dir = 6
        mergetype = "spatial"
        # -------------------------------
        self.template(index_of_dir, mergetype)

    # Standard case of one sub w/ 4 drives, spatial merge.
    def test_spatial_standard2(self):
        # ---- MergeTool() Arguments ----
        index_of_dir = 7
        mergetype = "spatial"
        # -------------------------------
        self.template(index_of_dir, mergetype)

    # Edge case in which the target directory only has one file.
    def test_spatial_one_file(self):
        # ---- MergeTool() Arguments ----
        index_of_dir = 8
        mergetype = "spatial"
        # -------------------------------
        self.template(index_of_dir, mergetype)

    # Edge case in which the target directory has no files. Expect program to warn the user, but not crash.
    def test_spatial_no_files(self):
        # ---- MergeTool() Arguments ----
        index_of_dir = 9
        mergetype = "spatial"
        # -------------------------------
        self.template(index_of_dir, mergetype)

    # ----- Helper Methods -----
    def template(self, desired_index, merge_type):
        """ Consistent code that will run between all test cases. Should work for both sequential and spatial.

        :param desired_index: Index of directory for this particular test case.
        :param merge_type: Type of merge, either Spatial or Sequential
        """
        print("Test: " + str(desired_index + 1) + " running...")
        desired_dir = self.getpath(desired_index)
        merged_data_path = desired_dir + "\\MergedData\\"

        merged_data_filelist = []

        # After this runs successfully, \MergedData\ will be populated.
        p_merge.MergeTool(desired_dir, merge_type)

        # Filelist is full paths to each merged file. Merged Subs will be a list of "Sub_*", to easily iterate later.
        # Both parameters are mutable, so no return value needed, will be changed in function.
        self.retrievemergeddata(merged_data_filelist, merged_data_path)

        # Now, filelist has full paths to all merged data. and sublist has all Subs merged.
        expected_list = self.expectedhandler(desired_index)

        for file in merged_data_filelist:
            sub = self.findsub(file)
            for expected_file in expected_list:
                if sub in expected_file:
                    merged_out_frame = pd.read_csv(file, sep='\s+', na_values='.', engine="c")
                    expected_out_frame = pd.read_csv(expected_file, sep='\s+', na_values='.', engine="c")

                    self.assertTrue(merged_out_frame.equals(expected_out_frame))
                    # out_frame = pd.read_csv(drive_group[0], sep='\s+', na_values='.', engine="c")

        # Clean MergedData so file retrieval is easy
        shutil.rmtree(merged_data_path)

    def getpath(self, index: int):
        """ Streamlines retrieving a given test case's "Merge Directory". Simply provides a full path.

        :param index: The location of the desired merge directory within the list, self.merge_dirs.
        :return: fullpath: string representing the completed path, based on the current working directory.
        """
        selected_dir = self.merge_dirs[index]
        fullpath = os.getcwd() + "\\tests\\MergeTools\\test_dats_to_merge\\" + selected_dir
        return fullpath

    def retrievemergeddata(self, file_list, current_dir ):
        """Load Merged Data directory full paths.

        :param file_list: List of full paths to files in \MergedData\
        """
        filelist = glob.glob(current_dir + '/*_Sub_*_Drive_*.dat')

        for file in filelist:
            file_list.append(file)

    def expectedhandler(self, index: int):
        """ Collects all information from the expected folders for comparison.

        :param index: Index of the current dir to be modified with the prefix, "expected_"
        :return filelist: Full list of paths in expected directory.
        """
        expected_dir = "expected_" + self.merge_dirs[index]
        fullpath = os.getcwd() + "\\tests\\MergeTools\\expected_csv\\" + expected_dir
        filelist = glob.glob(fullpath + '/*_Sub_*_Drive_*.dat')
        return filelist

    def findsub(self, filepath):
        """ Find particpant information from full filepath

        :param filepath: The full path to the file in question.
        :return: sub_str: a str that is "Sub_*" where '*' is the Sub Num for file path in question.
        """
        sub_index = filepath.find("Sub_")
        # Sub Numbers will be 2 digits, at most. So sub_str is allocated for the max sub num.
        sub_str = filepath[sub_index: sub_index + 6]

        # Check if the last place is an underscore, if so, we need to trim by 1 position.
        if sub_str[5] == '_':
            sub_str = sub_str[0: 5]

        return sub_str
