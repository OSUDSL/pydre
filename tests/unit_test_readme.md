# unit_test.py

unit_test.py is a testing tool implemented based on python 3.9.5 unit test framework. 
Additional Information of python unit test framework can be found at here: https://docs.python.org/3/library/unittest.html


# Run Unit Test

Command Line Syntax: `python -m tests.unit_test` under pydre directory.


# Helper Functions And Variables

### Variables
 - `self.ac_diff`: The acceptable difference between expected & actual results when testing scipy functions. Please see "Adding New Test Cases" for more information. 
 - `self.projectlist`: A list that contains names of required project files. All files in this list are expected to be present under `pydre\tests\test_projectfiles`.
 - `self.datalist`: A list that contains names of required data files. All files in this list are expected to be present under `pydre\tests\test_datfiles`.

### Helper Functions
 - `setUp()`: A function provided by unit test framework. The function executes before every test function (test case). 
 - `tearDown`: A function provided by unit test framework. The function executes after every test function (test case). 
 - `projectfileselect(index: int)`: Returns the path of self.projectlist[index].
 - `datafileselect(index: int)`: Returns the path of self.datalist[index].
 - `dd_to_str(drivedata: core.DriveData)`: Converts a drivedata object to a string. 

# Adding New Test Cases

Below is the basic structure of a test function:
```
def test_name(self):
    result = # actual output here
    expected_result = # expected output here
    self.assertEquals(result, expected_result)
```
A valid test function must have exactly one argument (which is self), and the name of a test function must begin with "test_". 
Actual result can be get from a function call, and expected result is usually hard coded. 
At least one assert function (usually self.assertEquals()) must be called to compare the actual result and expected result. More assert functions can be found at here: https://docs.python.org/3/library/unittest.html

### Testing scipy functions by using global variable `ac_diff`

Functions from scipy library are frequently used in pydre functions. It is possible that future version of scipy changes the implementations of some functions and provides more accurate results. Under this scenario, `self.assertEquals(result, expected_result)` will report an error, which is not what we want.
Therefore, a better approach is computing the difference between actual result and expected result and see if the difference is close enough to 0. Global variable `ac_diff` specifies the acceptable difference. 
Below are 2 ways of comparing scipy outputs:

 - `self.assertTrue(self.ac_diff > abs(expected_result - result))`
 - `assertLess(abs(expected_result - result), self.ac_diff)`

### Capturing stdout

By using io `library` and `contextlib` library, we can capture stdout and check the output by calling `self.assertIn(expected_console_output, actual_console output)`
Below is an example: 

```
def test_columnMatchException_1(self):
        f = io.StringIO()
        with contextlib.redirect_stderr(f):
            result = #function call
        expected_console_output = #expected result
        self.assertIn(expected_console_output, f.getvalue())
```


# Directories

 - `sample_pydre`: Contains an old version of pydre. sample_pydre.run will be called during the testing of pydre.run.
 - `test_datfiles`: Contains all the data files for testing. 
 - `test_projectfiles`: Contains all the project files for testing. 
