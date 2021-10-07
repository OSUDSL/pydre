import unittest
from pydre import project
import os
import glob


class WritableObject:
    def __init__(self):
        self.content = []

    def write(self, string):
        self.content.append(string)


class TestPydre(unittest.TestCase):

    def setUp(self):
        # self.whatever to access them in the rest of the script, runs before other scripts
        self.projectlist = ["test1_pf.json"]
        self.datalist = ["ExampleProject_Sub_1_Drive_1.dat"]

    def tearDown(self):
        pass
        # runs after all test cases, threw this in here just in case

    # ----- Test Cases -----
    def test_reftest(self):
        desiredproj = self.projectfileselect(0)
        p = project.Project(desiredproj)

        results = p.run(self.datafileselect(0))
        finalresults = results.to_string()
        expected_results = "Empty DataFrame\nColumns: [Subject, DriveID, ROI, meanVelocity, meanVelocity]\nIndex: []"
        self.assertEqual(finalresults, expected_results)

    # ----- Helper Methods -----
    def projectfileselect(self, index: int):
        projectfile = self.projectlist[index]
        fullpath = os.path.join(os.getcwd(), "test_projectfiles/", projectfile)
        return fullpath

    def datafileselect(self, index: int):
        datafile = self.datalist[index]

        fullpath = glob.glob(os.path.join(os.getcwd(), datafile))
        return fullpath
