import unittest
from pydre import project
from pydre import core
from pydre import filters
from pydre import metrics
import os
import glob
import contextlib
import io
from tests.sample_pydre import project as samplePD
import pandas
import numpy as np
from datetime import timedelta
import logging
import sys



class WritableObject:
    def __init__(self):
        self.content = []
        

    def write(self, string):
        self.content.append(string)

# Test cases of following functions are not included:
# Reason: unmaintained
# in common.py:
# tbiReaction()
# tailgatingTime() & tailgatingPercentage()
# ecoCar()
# gazeNHTSA()
#
# Reason: incomplete
# in common.py:
# findFirstTimeOutside()
# brakeJerk()

class TestPydre(unittest.TestCase):
    
    ac_diff = 0.000001  
    # the acceptable difference between expected & actual results when testing scipy functions


    def setUp(self):
        # self.whatever to access them in the rest of the script, runs before other scripts
        self.projectlist = ["honda.json"]
        self.datalist = ["Speedbump_Sub_8_Drive_1.dat", "ColTest_Sub_10_Drive_1.dat"]
        self.zero = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        funcName = ' [ ' + self._testMethodName + ' ] ' # the name of test function that will be executed right after this setUp()
        print(' ')
        print (funcName.center(80,'#'))
        print(' ')

    def tearDown(self):
        print(' ')
        print('[ END ]'.center(80, '#'))
        print(' ')

    # ----- Helper Methods -----
    def projectfileselect(self, index: int):
        projectfile = self.projectlist[index]
        fullpath = os.path.join("tests/test_projectfiles/", projectfile)
        return fullpath

    def datafileselect(self, index: int):
        datafile = self.datalist[index]
        fullpath = glob.glob(os.path.join(os.getcwd(), "tests/test_datfiles/", datafile))
        return fullpath

    def secs_to_timedelta(self, secs):
        return timedelta(weeks=0, days=0, hours=0, minutes=0, seconds=secs)

    def compare_cols(self, result_df, expected_df, cols):
        result = True
        for names in cols:
            result = result and result_df[names].equals(expected_df[names])
            if not result:
                print(names)
                print(result_df[names])
                print("===")
                print(expected_df[names])
                return False
        return result
    
    # convert a drivedata object to a str
    def dd_to_str(self, drivedata: core.DriveData):
        output = ""
        output += str(drivedata.PartID)
        output += str(drivedata.DriveID)
        output += str(drivedata.roi)
        output += str(drivedata.data)
        output += str(drivedata.sourcefilename)
        return output

    # ----- Test Cases -----
    def test_datafile_exist(self):
        datafiles = self.datafileselect(0)
        self.assertFalse(0 == len(datafiles))
        for f in datafiles:
            self.assertTrue(os.path.isfile(f))

    def test_reftest(self):
    	
        desiredproj = self.projectfileselect(0)
        p = project.Project(desiredproj)

        results = p.run(self.datafileselect(0))
        results.Subject.astype('int64')

        sample_p = samplePD.Project(desiredproj)
        expected_results = (sample_p.run(self.datafileselect(0)))
        self.assertTrue(self.compare_cols(results, expected_results, ['ROI', 'getTaskNum']))

    def test_columnMatchException_excode(self):
        f = io.StringIO()
        with self.assertRaises(SystemExit) as cm:
            desiredproj = self.projectfileselect(0)
            p = project.Project(desiredproj)
            result = p.run(self.datafileselect(1))
        self.assertEqual(cm.exception.code, 1)

    def test_columnMatchException_massage(self):
        d3 = {'DatTime': [0.017, 0.034, 0.05, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184]}

        df = pandas.DataFrame(data=d3)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")
        handler = logging.FileHandler(filename='tests\\temp.log')
        filters.logger.addHandler(handler)
        with self.assertRaises(core.ColumnsMatchError): 
            result = filters.smoothGazeData(data_object)
        expected_console_output = "Can't find needed columns {'FILTERED_GAZE_OBJ_NAME'} in data file ['test_file3.csv'] | function: smoothGazeData"
       
        temp_log = open('tests\\temp.log')
        msg_list = temp_log.readlines()
        msg = ' '.join(msg_list)
        filters.logger.removeHandler(handler)
        #self.assertIn(expected_console_output, msg)



    #Isolate this test case No more sliceByTime Function in pydre.core
    #def test_core_sliceByTime_1(self):
        #d = {'col1': [1, 2, 3, 4, 5, 6], 'col2': [7, 8, 9, 10, 11, 12]}
        #df = pandas.DataFrame(data=d)
        #result = (core.sliceByTime(1, 3, "col1", df).to_string()).lstrip()
        #expected_result = "col1  col2\n0     1     7\n1     2     8\n2     3     9"
        #self.assertEqual(result, expected_result)

    #Isolate this test case No more sliceByTime Function in pydre.core
    #def test_core_sliceByTime_2(self):
        #d = {'col1': [1, 1.1, 3, 4, 5, 6], 'col2': [7, 8, 9, 10, 11, 12]}
        #df = pandas.DataFrame(data=d)
        #result = (core.sliceByTime(1, 2, "col1", df).to_string()).lstrip()
        #expected_result = "col1  col2\n0   1.0     7\n1   1.1     8"
        #self.assertEqual(result, expected_result)
    
    def test_core_mergeBySpace(self):
        d1 = {'SimTime': [1, 2], 'XPos': [1, 3], 'YPos': [4, 3]}
        df1 = pandas.DataFrame(data=d1)

        d2 = {'SimTime': [3, 4], 'XPos': [10, 12], 'YPos': [15, 16]}
        df2 = pandas.DataFrame(data=d2)

        data_object1 = core.DriveData( data=df1, sourcefilename="test_file.csv")
        data_object2 = core.DriveData.initV2(PartID=0, DriveID=2, data=df2, sourcefilename="test_file.csv")

        param = []
        param.append(data_object1)
        param.append(data_object2)
        result = self.dd_to_str(core.mergeBySpace(param))
        expected_result = "0[1, [2]]None[   SimTime  XPos  YPos\n0        1     1     4\n1        2     3     3\n0        2    10    15\n1        3    12    16]['test_file.csv', ['test_file.csv']]"
        self.assertEqual(result, expected_result)

    def test_filter_numberSwitchBlocks_1(self):
        d = {'DatTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
              'TaskStatus': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]} #input
        df = pandas.DataFrame(data=d)
        data_object3 = core.DriveData( data=df, sourcefilename="test_file3.csv")
        result = filters.numberSwitchBlocks(drivedata=data_object3)
        
        expected = {'DatTime': [0.017, 0.034, 0.05, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
        'TaskStatus': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
        'taskblocks': [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]}
        expected_result_df = pandas.DataFrame(data=expected)
        expected_result = core.DriveData( data=expected_result_df, sourcefilename="test_file3.csv")
        
        print(result.data)
        print(expected_result.data)

        self.assertEqual(len(result.data), len(expected_result.data))
        self.assertTrue((self.compare_cols(expected_result.data, result.data, ['DatTime', 'TaskStatus', 'taskblocks'])))
        self.assertEqual(result.sourcefilename, expected_result.sourcefilename)

    def test_filter_numberSwitchBlocks_2(self):
        d = {'DatTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
              'TaskStatus': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]} #input
        df = pandas.DataFrame(data=d)
        data_object3 = core.DriveData( data=df, sourcefilename="test_file3.csv")
        result = filters.numberSwitchBlocks(drivedata=data_object3)
        #print(result.to_string())
        expected = {'DatTime': [0.017, 0.034, 0.05, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
        'TaskStatus': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
        'taskblocks': [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]}
        expected_result_df = pandas.DataFrame(data=expected)
        expected_result = core.DriveData( data=expected_result_df, sourcefilename="test_file3.csv")
        self.assertEqual(len(result.data), len(expected_result.data))
        self.assertTrue((self.compare_cols(expected_result.data, result.data, ['DatTime', 'TaskStatus', 'taskblocks'])))
        self.assertEqual(result.sourcefilename, expected_result.sourcefilename)

    def test_filter_numberSwitchBlocks_3(self):
        d = {'DatTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
              'TaskStatus': [0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0]} #input
        df = pandas.DataFrame(data=d)
        data_object3 = core.DriveData( data=df, sourcefilename="test_file3.csv")

        result = filters.numberSwitchBlocks(drivedata=data_object3)
        #print(result.to_string())
        expected = {'DatTime': [0.017, 0.034, 0.05, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
        'TaskStatus': [0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0], 
        'taskblocks': [np.nan, np.nan, np.nan, np.nan, np.nan, 1.0, 1.0, 1.0, 1.0, np.nan, np.nan]}
        expected_result_df = pandas.DataFrame(data=expected)
        expected_result = core.DriveData( data=expected_result_df, sourcefilename="test_file3.csv")
        self.assertEqual(len(result.data), len(expected_result.data))
        self.assertTrue((self.compare_cols(expected_result.data, result.data, ['DatTime', 'TaskStatus', 'taskblocks'])))
        self.assertEqual(result.sourcefilename, expected_result.sourcefilename)

    
    def test_filter_smoothGazeData_1(self): 
        d3 = {'DatTime': [0.017, 0.034, 0.05, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
              'FILTERED_GAZE_OBJ_NAME': ['localCS.CSLowScreen', 'localCS.CSLowScreen', 'localCS.CSLowScreen', 
                          'localCS.CSLowScreen', 'localCS.CSLowScreen', 'localCS.CSLowScreen', 
                           'localCS.CSLowScreen', 'localCS.CSLowScreen', 'localCS.CSLowScreen', 
                             'localCS.CSLowScreen', 'localCS.CSLowScreen']}
        # the func should be able to identify this in-valid input and returns None after prints 
        # "Bad gaze data, not enough variety. Aborting"
        print("expected console output: Bad gaze data, not enough variety. Aborting")

        df = pandas.DataFrame(data=d3)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")

        result = filters.smoothGazeData(data_object)
        #print(result.to_string())
        self.assertEqual(None, result)


    def test_filter_smoothGazeData_2(self):
        d3 = {'DatTime': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8,
        1.9, 2.0, 2.1, 2.2, 2.3, 2.4], 
        'FILTERED_GAZE_OBJ_NAME': ['localCS.dashPlane', 'localCS.dashPlane', 'localCS.dashPlane', 
        'localCS.dashPlane', 'localCS.WindScreen', 'localCS.WindScreen', 
        'localCS.WindScreen', 'localCS.WindScreen', 'localCS.WindScreen', 
        'localCS.WindScreen', 'localCS.WindScreen', 'localCS.WindScreen', 
        'localCS.WindScreen', 'localCS.WindScreen', 'localCS.WindScreen', 
        'localCS.dashPlane', 'localCS.dashPlane', 'localCS.dashPlane',
        'localCS.dashPlane', 'localCS.dashPlane', 'localCS.dashPlane',
        'localCS.dashPlane', 'localCS.dashPlane', 'localCS.dashPlane']}

        df = pandas.DataFrame(data=d3)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")
        
        result = filters.smoothGazeData(data_object, latencyShift=0)
        
        dat_time_col = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8,
        1.9, 2.0, 2.1, 2.2, 2.3, 2.4]
        timedelta_col = []
        for t in dat_time_col:
            timedelta_col.append(self.secs_to_timedelta(t))
        expected = {'timedelta': timedelta_col, 'DatTime': dat_time_col,  
        'FILTERED_GAZE_OBJ_NAME': ['localCS.dashPlane', 'localCS.dashPlane', 'localCS.dashPlane', 
        'localCS.dashPlane', 'localCS.WindScreen', 'localCS.WindScreen', 
        'localCS.WindScreen', 'localCS.WindScreen', 'localCS.WindScreen', 
        'localCS.WindScreen', 'localCS.WindScreen', 'localCS.WindScreen', 
        'localCS.WindScreen', 'localCS.WindScreen', 'localCS.WindScreen', 
        'localCS.dashPlane', 'localCS.dashPlane', 'localCS.dashPlane',
        'localCS.dashPlane', 'localCS.dashPlane', 'localCS.dashPlane',
        'localCS.dashPlane', 'localCS.dashPlane', 'localCS.dashPlane'], 
        'gaze': ["offroad", "offroad", "offroad", "offroad", "onroad", "onroad", "onroad", "onroad", "onroad", "onroad", "onroad", 
        "onroad", "onroad", "onroad", "onroad", "offroad", "offroad", "offroad", "offroad", "offroad", "offroad", "offroad", "offroad", 
        "offroad"], 
        'gazenum': np.array([1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3], dtype=np.int32)}

        expected_result_df = pandas.DataFrame(data=expected)
        
        self.assertTrue(expected_result_df.equals(result.data));
        #self.assertTrue(self.compare_cols(result.data[0], expected_result_df, ['DatTime', 'FILTERED_GAZE_OBJ_NAME', 'gaze', 'gazenum']))

    def test_filter_smoothGazeData_3(self):
        # --- Construct input ---
        dat_time_col = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8,
        1.9, 2.0, 2.1, 2.2, 2.3, 2.4]
        gaze_col = ['localCS.dashPlane', 'localCS.dashPlane', 'localCS.dashPlane', 
        'localCS.dashPlane', 'localCS.WindScreen', 'localCS.dashPlane', 
        'localCS.WindScreen', 'localCS.dashPlane', 'localCS.WindScreen', 
        'localCS.dashPlane', 'localCS.WindScreen', 'localCS.dashPlane', 
        'localCS.WindScreen', 'localCS.dashPlane', 'localCS.WindScreen', 
        'localCS.dashPlane', 'localCS.dashPlane', 'localCS.dashPlane',
        'localCS.dashPlane', 'localCS.dashPlane', 'localCS.dashPlane',
        'localCS.dashPlane', 'localCS.dashPlane', 'localCS.dashPlane']

        d3 = {'DatTime': dat_time_col, 'FILTERED_GAZE_OBJ_NAME': gaze_col}

        df = pandas.DataFrame(data=d3)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")
        # ----------------------
        result = filters.smoothGazeData(data_object, latencyShift=0)
        print(result.data)
        
        timedelta_col = []
        for t in dat_time_col:
            timedelta_col.append(self.secs_to_timedelta(t))
        expected = {'timedelta': timedelta_col, 'DatTime': dat_time_col,  
        'FILTERED_GAZE_OBJ_NAME': gaze_col, 
        'gaze': ["offroad", "offroad", "offroad", "offroad", "offroad", "offroad", 
        "offroad", "offroad", "offroad", "offroad", "offroad", "offroad", 
        "offroad", "offroad", "offroad", "offroad", "offroad", "offroad", 
        "offroad", "offroad", "offroad", "offroad", "offroad", "offroad"], 
        'gazenum': np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], dtype=np.int32)}

        expected_result_df = pandas.DataFrame(data=expected)
        
        self.assertTrue(expected_result_df.equals(result.data));
        #self.assertTrue(self.compare_cols(result.data[0], expected_result_df, ['DatTime', 'FILTERED_GAZE_OBJ_NAME', 'gaze', 'gazenum']))


    def test_metrics_findFirstTimeAboveVel_1(self):
    	# --- construct input ---
        d = {'DatTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
              'Velocity': [-0.000051, -0.000051, -0.000041, -0.000066, -0.000111, -0.000158, -0.000194, -0.000207, 0.000016, 0.000107, 0.000198]} #input
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------

        result = metrics.common.findFirstTimeAboveVel(data_object)
        expected_result = -1
        self.assertEqual(expected_result, result)


    def test_metrics_findFirstTimeAboveVel_2(self):
    	# --- construct input ---
        d = {'DatTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
              'Velocity': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]} #input
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------
        
        result = metrics.common.findFirstTimeAboveVel(data_object)
        expected_result = -1
        self.assertEqual(expected_result, result)
        


    def test_metrics_findFirstTimeAboveVel_3(self):
    	# --- construct input ---
        d = {'DatTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
              'Velocity': [0, 20.1, 21.0, 22.0, 23.12, 25.1, 26.3, 27.9, 30.1036, 31.3, 32.5]} #input
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------

        result = metrics.common.findFirstTimeAboveVel(data_object)
        expected_result = 5
        self.assertEqual(expected_result, result)

    def test_metrics_findFirstTimeAboveVel_4(self):
    	# --- construct input ---
        d = {'DatTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
              'Velocity': [25, 25, 25, 25, 25, 25, 25, 25, 25, 25, 25]} #input
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------

        result = metrics.common.findFirstTimeAboveVel(data_object)
        expected_result = 0
        self.assertEqual(expected_result, result)

    def test_metrics_findFirstTimeOutside_1(self):
        pass
        # --- construct input ---
        d = {'SimTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
              'position': [0, 20.1, 21.0, 22.0, 23.12, 25.1, 26.3, 27.9, 30.1036, 31.3, 32.5]} #input
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------

        #result = metrics.common.findFirstTimeOutside(data_object)
        #expected_result = 0
        #self.assertEqual(expected_result, result)

        #err: NameError: name 'pos' is not defined --------------------------------------------------------!!!!!!!!!

    def test_metrics_colMean_1(self):
        # --- construct input ---
        d = {'SimTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
              'position': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]} #input
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------
        
        result = metrics.common.colMean(data_object, 'position')
        expected_result = 5
        self.assertEqual(expected_result, result)


    def test_metrics_colMean_2(self):
        # --- construct input ---
        d = {'SimTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
              'position': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]} #input
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------
        
        result = metrics.common.colMean(data_object, 'position', 3)
        expected_result = 6.5
        self.assertEqual(expected_result, result)


    def test_metrics_colMean_3(self):
        # --- construct input ---
        d = {'SimTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
              'position': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]} #input
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------
        
        result = metrics.common.colMean(data_object, 'position', 3)
        expected_result = np.nan
        #self.assertEqual(expected_result, result)
        np.testing.assert_equal(expected_result, result)


    def test_metrics_colSD_1(self):
        # --- construct input ---
        d = {'SimTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
              'position': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]} #input
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------

        result = metrics.common.colSD(data_object, 'position')
        expected_result = 3.1622776601683795
        self.assertTrue(self.ac_diff > abs(expected_result - result))


    def test_metrics_colSD_2(self):
        # --- construct input ---
        d = {'SimTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
              'position': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]} #input
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------

        result = metrics.common.colSD(data_object, 'position', 3)
        expected_result = 2.29128784747792
        self.assertTrue(self.ac_diff > abs(expected_result - result))


    def test_metrics_colSD_3(self):
        # --- construct input ---
        d = {'SimTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
              'position': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]} #input
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------

        result = metrics.common.colSD(data_object, 'position')
        expected_result = 0
        self.assertTrue(self.ac_diff > abs(expected_result - result))


    def test_metrics_colMax_1(self):
        # --- construct input ---
        d = {'SimTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
              'position': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]} #input
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------

        result = metrics.common.colMax(data_object, 'position')
        expected_result = 10
        self.assertEqual(expected_result, result)

    def test_metrics_colMax_2(self):
        # --- construct input ---
        d = {'SimTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
              'position': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9]} #input
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------

        result = metrics.common.colMax(data_object, 'position')
        expected_result = 9
        self.assertEqual(expected_result, result)
    
    def test_metrics_colMax_3(self):
        # --- construct input ---
        d = {'SimTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
              'position': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]} #input
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------

        result = metrics.common.colMax(data_object, 'position')
        expected_result = 0
        self.assertEqual(expected_result, result)

    def test_metrics_colMin_1(self):
        # --- construct input ---
        d = {'SimTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
              'position': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]} #input
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------

        result = metrics.common.colMin(data_object, 'position')
        expected_result = 0
        self.assertEqual(expected_result, result)

    def test_metrics_colMin_2(self):
        # --- construct input ---
        d = {'SimTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
              'position': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]} #input
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------

        result = metrics.common.colMin(data_object, 'position')
        expected_result = 0
        self.assertEqual(expected_result, result)
    

    def test_metrics_timeAboveSpeed_1(self):
        # --- construct input ---
        d = {'SimTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
              'Velocity': [0, 20.1, 21.0, 22.0, 23.12, 25.1, 26.3, 27.9, 30.1036, 31.3, 32.5]} #input
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------
        
        result = metrics.common.timeAboveSpeed(data_object, 0, True)
        expected_result = 1.002994011976048
        self.assertTrue(self.ac_diff > abs(expected_result - result))

    def test_metrics_timeAboveSpeed_2(self):
        # --- construct input ---
        d = {'SimTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
              'Velocity': [0, 20.1, 21.0, 22.0, 23.12, 25.1, 26.3, 27.9, 30.1036, 31.3, 32.5]} #input
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData(data=df, sourcefilename="test_file3.csv")
        # -----------------------
        
        result = metrics.common.timeAboveSpeed(data_object, 0, False)
        expected_result = 0.1675
        self.assertTrue(self.ac_diff > abs(expected_result - result))

    def test_metrics_timeAboveSpeed_3(self):
        # --- construct input ---
        d = {'SimTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
              'Velocity': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]} #input
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------
        
        result = metrics.common.timeAboveSpeed(data_object, 0, False)
        expected_result = 0.0
        self.assertTrue(self.ac_diff > abs(expected_result - result))

    def test_metrics_roadExits_1(self):
        # --- construct input ---
        d = {'SimTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
              'RoadOffset': [1.7679, 1.7679, 1.5551, 1.5551, 1.5551, 1.667174, 1.667174, 1.668028, 1.668028, 1.668028, 1.786122], 
               'Velocity': [0, 20.1, 21.0, 22.0, 23.12, 25.1, 26.3, 27.9, 30.1036, 31.3, 32.5]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------
        
        result = metrics.common.roadExits(data_object)
        expected_result = 0
        self.assertEqual(expected_result, result)

    def test_metrics_roadExits_2(self):
        # --- construct input ---
        d = {'SimTime': [0.017, 0.034, 0.05, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
           'RoadOffset': [7.3, 7.4, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2], 
             'Velocity': [0, 15.1, 20.1, 21.0, 22.0, 23.12, 25.1, 26.3, 27.9, 30.1036, 31.3]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------
        
        result = metrics.common.roadExits(data_object)
        expected_result = 0.034 
        self.assertEqual(expected_result, result)


    def test_metrics_roadExits_3(self):
        # --- construct input ---
        d = {'SimTime': [0.017, 0.034, 0.05, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
           'RoadOffset': [-1, -1, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2], 
             'Velocity': [15.1, 20.1, 21.0, 22.0, 23.12, 25.1, 26.3, 27.9, 30.1036, 31.3, 32.5]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------
        
        result = metrics.common.roadExits(data_object)
        expected_result = 0.034
        self.assertEqual(expected_result, result)

    def test_metrics_roadExitsY_1(self):
        # --- construct input ---
        d = {'SimTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
              'YPos': [1.7679, 1.7679, 1.5551, 1.5551, 1.5551, 1.667174, 1.667174, 1.668028, 1.668028, 1.668028, 1.786122], 
               'Velocity': [0, 20.1, 21.0, 22.0, 23.12, 25.1, 26.3, 27.9, 30.1036, 31.3, 32.5]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------
        
        result = metrics.common.roadExitsY(data_object)
        expected_result = 0
        self.assertEqual(expected_result, result)

    def test_metrics_roadExitsY_2(self):
        # --- construct input ---
        d = {'SimTime': [0.017, 0.034, 0.05, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
           'YPos': [7.3, 7.4, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2], 
             'Velocity': [0, 15.1, 20.1, 21.0, 22.0, 23.12, 25.1, 26.3, 27.9, 30.1036, 31.3]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------
        
        result = metrics.common.roadExitsY(data_object)
        expected_result = 0.184 
        self.assertEqual(expected_result, result)


    def test_metrics_roadExitsY_3(self):
        # --- construct input ---
        d = {'SimTime': [0.017, 0.034, 0.05, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
           'YPos': [-1, -1, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2, 7.2], 
             'Velocity': [15.1, 20.1, 21.0, 22.0, 23.12, 25.1, 26.3, 27.9, 30.1036, 31.3, 32.5]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------
        
        result = metrics.common.roadExitsY(data_object)
        expected_result = 0.184
        self.assertEqual(expected_result, result)


    def test_metrics_steeringEntropy_1(self):
        # --- construct input ---
        d = {'SimTime': [0.017, 0.034, 0.05, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
             'Steer': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------
        
        result = metrics.common.steeringEntropy(data_object)
        expected_result = 0.0
        self.assertEqual(expected_result, result)


    def test_metrics_steeringEntropy_2(self):
        # --- construct input ---
        d = {'SimTime': [0.017, 0.034, 0.05, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
             'Steer': [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------
        
        result = metrics.common.steeringEntropy(data_object)
        expected_result = 0.17147549009906388
        self.assertEqual(expected_result, result)


    def test_metrics_numOfErrorPresses_1(self):
        # --- construct input ---
        d = {'SimTime': [0.017, 0.034, 0.05, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
             'TaskFail': [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")
        # -----------------------

        result = metrics.common.numOfErrorPresses(data_object)
        expected_result = 1
        self.assertEqual(expected_result, result)
    

    def test_metrics_numOfErrorPresses_2(self):
        # --- construct input ---
        d = {'SimTime': [0.017, 0.034, 0.05, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
             'TaskFail': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")
        # -----------------------

        result = metrics.common.numOfErrorPresses(data_object)
        expected_result = 0
        self.assertEqual(expected_result, result)

    def test_metrics_firstOccurance_1(self):
        # --- construct input ---

        df = pandas.DataFrame({"Col1": [10, 20, 15, 30, 45],
                   "Col2": [13, 23, 18, 33, 48],
                   "Col3": [17, 27, 22, 37, 52]},
                  index=[1, 2, 3, 4, 5])
        
        # -----------------------

        result = metrics.common.firstOccurance(df, 'Col1')
        expected_result = 1
        print("======", result)
        self.assertEqual(expected_result, result)


    def test_metrics_lanePosition_sdlp_1(self):
        d = {'SimTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
         'DatTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
          'LaneOffset': [1.7679, 1.7679, 1.7679, 1.7679, 1.7679, 1.667689, 1.667689, 1.666987, 
           1.666987, 1.665995, 1.664588], 
           'Lane': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")

        result = metrics.common.lanePosition(data_object, laneInfo="sdlp")
        expected_result = 0.050418838619299945
        self.assertTrue(self.ac_diff > abs(expected_result - result))


    def test_metrics_lanePosition_mean_1(self):
        d = {'SimTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
         'DatTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
          'LaneOffset': [1.7679, 1.7679, 1.7679, 1.7679, 1.7679, 1.667689, 1.667689, 1.666987, 
           1.666987, 1.665995, 1.664588], 
           'Lane': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")

        result = metrics.common.lanePosition(data_object, laneInfo="mean")
        expected_result = 1.712675909090909
        self.assertTrue(self.ac_diff > abs(expected_result - result))
    
    def test_metrics_lanePosition_mean_2(self):
        d = {'SimTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
         'DatTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
          'LaneOffset': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
          'Lane': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")

        result = metrics.common.lanePosition(data_object, laneInfo="mean")
        expected_result = 0
        self.assertTrue(self.ac_diff > abs(expected_result - result))
    
    
    def test_metrics_lanePosition_msdlp_1(self):
        d = {'SimTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
         'DatTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
          'LaneOffset': [1.7679, 1.7679, 1.7679, 1.7679, 1.7679, 1.667689, 1.667689, 1.666987, 
           1.666987, 1.665995, 1.664588], 
           'Lane': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")

        result = metrics.common.lanePosition(data_object, laneInfo="msdlp")
        expected_result = 0.11609391266118639
        self.assertTrue(self.ac_diff > abs(expected_result - result))

    def test_metrics_lanePosition_msdlp_2(self):
        d = {'SimTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
         'DatTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
          'LaneOffset': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
          'Lane': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")

        result = metrics.common.lanePosition(data_object, laneInfo="msdlp")
        expected_result = 0
        self.assertTrue(self.ac_diff > abs(expected_result - result))

    def test_metrics_lanePosition_msdlp_noiseremove1(self):
        d = {'SimTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
         'DatTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
          'LaneOffset': [1.7679, 1.7679, 1.7679, 1.7679, 1.7679, 1.667689, 1.667689, 1.666987, 
           1.666987, 1.665995, 1.664588], 
           'Lane': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")

        result = metrics.common.lanePosition(data_object, laneInfo="msdlp", noisy="true")
        expected_result = 0.3609804008333242
        self.assertTrue(self.ac_diff > abs(expected_result - result))

    def test_metrics_lanePosition_msdlp_noiseremove2(self):
        d = {'SimTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
         'DatTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
          'LaneOffset': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
          'Lane': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")

        result = metrics.common.lanePosition(data_object, laneInfo="msdlp", noisy="true")
        expected_result = 0
        self.assertTrue(self.ac_diff > abs(expected_result - result))

    def test_metrics_lanePosition_msdlp_filtfilt1(self):
        d = {'SimTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
         'DatTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
          'LaneOffset': [1.7679, 1.7679, 1.7679, 1.7679, 1.7679, 1.667689, 1.667689, 1.666987, 
           1.666987, 1.665995, 1.664588], 
           'Lane': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")

        result = metrics.common.lanePosition(data_object, laneInfo="msdlp", filtfilt="true")
        expected_result = 0.04134629214979945
        self.assertTrue(self.ac_diff > abs(expected_result - result))

    def test_metrics_lanePosition_msdlp_filtfilt2(self):
        d = {'SimTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
         'DatTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
          'LaneOffset': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
          'Lane': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")

        result = metrics.common.lanePosition(data_object, laneInfo="msdlp", filtfilt="true")
        expected_result = 0
        self.assertTrue(self.ac_diff > abs(expected_result - result))


    def test_metrics_lanePosition_msdlp_violationDuration1(self):
        d = {'SimTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
         'DatTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
          'LaneOffset': [1.7679, 1.7679, 1.7679, 1.7679, 1.7679, 1.667689, 1.667689, 1.666987, 
           1.666987, 1.665995, 1.664588], 
           'Lane': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")

        result = metrics.common.lanePosition(data_object, laneInfo="violation_duration")
        expected_result = 0.17000000000000004
        self.assertTrue(self.ac_diff > abs(expected_result - result))

    def test_metrics_lanePosition_msdlp_violationDuration2(self):
        d = {'SimTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
         'DatTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
          'LaneOffset': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
          'Lane': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")

        result = metrics.common.lanePosition(data_object, laneInfo="violation_duration")
        expected_result = 0
        self.assertTrue(self.ac_diff > abs(expected_result - result))

    def test_metrics_lanePosition_msdlp_exits1(self):
        d = {'SimTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
         'DatTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
          'LaneOffset': [1.7679, 1.7679, 1.7679, 1.7679, 1.7679, 1.667689, 1.667689, 1.666987, 
           1.666987, 1.665995, 1.664588], 
           'Lane': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")

        result = metrics.common.lanePosition(data_object, laneInfo="exits")
        expected_result = 0.15000000000000002
        self.assertTrue(self.ac_diff > abs(expected_result - result))

    def test_metrics_lanePosition_msdlp_exits2(self):
        d = {'SimTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
         'DatTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
          'LaneOffset': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
          'Lane': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")

        result = metrics.common.lanePosition(data_object, laneInfo="exits")
        expected_result = 0
        self.assertTrue(self.ac_diff > abs(expected_result - result))

    def test_metrics_lanePosition_violationCount(self):
        d = {'SimTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
         'DatTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
          'LaneOffset': [11.1, 11.1, 0, 0, 11.5, 11.667689, 11.7, 11.8, 11.9, 12.0, 12.1], 
            'Lane': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")

        result = metrics.common.lanePosition(data_object, laneInfo="violation_count")
        expected_result = 1
        self.assertEqual(expected_result, result)
    
    def test_metrics_crossCorrelate_1(self):
        # --- construct input ---
        d = {'SimTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
         'DatTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
         'HeadwayTime': [11.1, 11.1, 0, 0, 11.5, 11.667689, 11.7, 11.8, 11.9, 12.0, 12.1], 
         'XPos': self.zero}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")
        result = metrics.common.crossCorrelate(data_object)
        # -----------------------
        expected_result = 0

        self.assertEqual(expected_result, result)


    def test_metrics_getTaskNum_1(self):
        # --- construct input ---
        d = {'TaskNum': [0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")
        # -----------------------

        result = metrics.common.getTaskNum(data_object)
        expected_result = 0
        self.assertEqual(expected_result, result)

    def test_metrics_boxMetrics_count_1(self):
        # --- Construct input ---
        d3 = {'SimTime': [0.017, 0.034, 0.05, 0.067, 0.084, 0.084, 0.117, 0.134, 0.149, 0.166, 0.184], 
             'FeedbackButton': [0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 0], 
             'BoxAppears': [0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0]}
        df = pandas.DataFrame(data=d3)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")
        # -----------------------

        result = metrics.common.boxMetrics(data_object)
        expected_result = 2
        self.assertEqual(expected_result, result)

    def test_metrics_boxMetrics_count_2(self):
        # --- Construct input ---
        d3 = {'SimTime': [0.017, 0.034, 0.05, 0.067, 0.084, 0.084, 0.117, 0.134, 0.149, 0.166, 0.184], 
             'FeedbackButton': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
             'BoxAppears': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}
        df = pandas.DataFrame(data=d3)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")
        # -----------------------

        result = metrics.common.boxMetrics(data_object)
        expected_result = 0
        self.assertEqual(expected_result, result)

    def test_metrics_boxMetrics_mean_1(self):
        # --- Construct input ---
        d3 = {'SimTime': [0.017, 0.034, 0.05, 0.067, 0.084, 0.084, 0.117, 0.134, 0.149, 0.166, 0.184], 
             'FeedbackButton': [0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 0], 
            'BoxAppears': [0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0]}
        df = pandas.DataFrame(data=d3)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")
        # -----------------------

        result = metrics.common.boxMetrics(data_object, stat='mean')
        expected_result = 0.015999999999999993
        self.assertTrue(self.ac_diff > abs(expected_result - result))

    def test_metrics_boxMetrics_sd_1(self):
        # --- Construct input ---
        d3 = {'SimTime': [0.017, 0.034, 0.05, 0.067, 0.084, 0.084, 0.117, 0.134, 0.149, 0.166, 0.184], 
             'FeedbackButton': [0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 0], 
             'BoxAppears': [0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0]}
        df = pandas.DataFrame(data=d3)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")
        # -----------------------

        result = metrics.common.boxMetrics(data_object, stat='sd')
        expected_result = 0.0010000000000000078
        self.assertTrue(self.ac_diff > abs(expected_result - result))

    def test_metrics_crossCorrelate_1(self):
        # --- construct input ---
        d = {'SimTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
         'DatTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
         'HeadwayTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
         'XPos': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
         'OwnshipVelocity': [10, 11, 13, 14, 15, 17, 20, 23, 26, 29, 31], 
         'LeadCarVelocity': [13, 16, 18, 21, 25, 30, 32, 32.5, 34, 35, 37]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")
        # -----------------------

        result = metrics.common.crossCorrelate(data_object)
        expected_result = 0.9988164711609935

        self.assertTrue(self.ac_diff > abs(expected_result - result))

    def test_metrics_crossCorrelate_2(self):
        # --- construct input ---
        d = {'SimTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
         'DatTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
         'HeadwayTime': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
         'XPos': [0.52, 0.54, 0.55, 0.57, 0.59, 0.59, 0.6, 0.62, 0.64, 0.65, 0.67], 
         'OwnshipVelocity': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
         'LeadCarVelocity': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv")
        # -----------------------

        result = metrics.common.crossCorrelate(data_object)
        expected_result = 0

        self.assertEqual(expected_result, result)

    def test_metrics_speedbumpHondaGaze_1(self):
        # --- construct input ---
        d = {'DatTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
             'gaze': ['onroad', 'onroad', 'onroad', 'onroad', 
             'offroad', 'offroad', 'offroad', 'offroad', 
             'onroad', 'onroad', 'onroad'], 
             'gazenum': [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3], 
             'TaskFail': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
             'TaskID': [1, 1, 1, 2, 2, 3, 3, 3, 4, 5, 6],
             'TaskNum':  [1, 1, 1, 2, 2, 3, 3, 3, 4, 5, 6],
             'taskblocks': [1, 1, 1, 2, 2, 3, 3, 3, 4, 5, 6], 
             'PartID': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]} #input
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------

        result = metrics.common.speedbumpHondaGaze(data_object)
        expected_result = [0.085, 0.5089820359281438, 0.05, 0.0425]
        i = 0
        while (i < 4):
            self.assertTrue(self.ac_diff > abs(expected_result[i] - result[i]))
            i = i + 1

    def test_metrics_speedbumpHondaGaze_2(self):
        # --- construct input ---
        d = {'DatTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
             'gaze': ['onroad', 'onroad', 'onroad', 'onroad', 
             'onroad', 'onroad', 'onroad', 'onroad', 
             'onroad', 'onroad', 'onroad'], 
             'gazenum': [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3], 
             'TaskFail': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
             'TaskID': [1, 1, 1, 2, 2, 3, 3, 3, 4, 5, 6],
             'TaskNum':  [1, 1, 1, 2, 2, 3, 3, 3, 4, 5, 6],
             'taskblocks': [1, 1, 1, 2, 2, 3, 3, 3, 4, 5, 6], 
             'PartID': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]} #input
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------

        result = metrics.common.speedbumpHondaGaze(data_object)
        expected_result = [0.135, 0.8083832335329343, np.nan, 0.045000000000000005]
        i = 0
        while (i < 4):
            if (np.isnan(result[i])):
                np.testing.assert_equal(expected_result[i], result[i])
            else:
                self.assertTrue(self.ac_diff > abs(expected_result[i] - result[i]))
            i = i + 1


    def test_metrics_speedbumpHondaGaze_3(self):
        # --- construct input ---
        d = {'DatTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
             'gaze': ['onroad', 'onroad', 'onroad', 'onroad', 
             'onroad', 'onroad', 'onroad', 'onroad', 
             'onroad', 'onroad', 'onroad'], 
             'gazenum': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
             'TaskFail': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
             'TaskID': [1, 1, 1, 2, 2, 3, 3, 3, 4, 5, 6],
             'TaskNum':  [1, 1, 1, 2, 2, 3, 3, 3, 4, 5, 6],
             'taskblocks': [1, 1, 1, 2, 2, 3, 3, 3, 4, 5, 6], 
             'PartID': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]} #input
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------

        result = metrics.common.speedbumpHondaGaze(data_object)
        expected_result = [0.16699999999999998, 1.0, np.nan, 0.16699999999999998]
        i = 0
        while (i < 4):
            if (np.isnan(result[i])):
                np.testing.assert_equal(expected_result[i], result[i])
            else:
                self.assertTrue(self.ac_diff > abs(expected_result[i] - result[i]))
            i = i + 1

    def test_metrics_speedbumpHondaGaze_4(self):
        # --- construct input ---
        d = {'DatTime': [0.017, 0.034, 0.050, 0.067, 0.084, 0.1, 0.117, 0.134, 0.149, 0.166, 0.184], 
             'gaze': ['offroad', 'offroad', 'offroad', 'offroad', 'offroad', 'offroad', 'offroad', 'offroad', 'offroad', 'offroad', 'offroad'], 
             'gazenum': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
             'TaskFail': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
             'TaskID': [1, 1, 1, 2, 2, 3, 3, 3, 4, 5, 6],
             'TaskNum':  [1, 1, 1, 2, 2, 3, 3, 3, 4, 5, 6],
             'taskblocks': [1, 1, 1, 2, 2, 3, 3, 3, 4, 5, 6], 
             'PartID': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]} #input
        df = pandas.DataFrame(data=d)
        data_object = core.DriveData( data=df, sourcefilename="test_file3.csv") 
        # -----------------------

        result = metrics.common.speedbumpHondaGaze(data_object)
        expected_result = [0.0, 0.0, 0.16699999999999998, np.nan]
        i = 0
        while (i < 4):
            if (np.isnan(result[i])):
                np.testing.assert_equal(expected_result[i], result[i])
            else:
                self.assertTrue(self.ac_diff > abs(expected_result[i] - result[i]))
            i = i + 1


if __name__ == '__main__':
    #print("list: ", glob.glob(os.path.join(os.getcwd(),  "ExampleProject_Sub_1_Drive_1.dat")))

    unittest.main()