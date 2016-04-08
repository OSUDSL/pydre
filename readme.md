# pydre_run.py

This script is a front end application that allows the user to analyze data using command line arguments.

The user must enter the path for the project file and data file in order to aggregate the data. The user has the option of specifying an output file name, to which the test results will be saved. If no output file name is given the output will save to _"out.csv"_ by default. A brief description of the aforementioned arguments is offered below.

Command Line Arguments:

  * Project File [-p]: The project file contains the regions of interest from which the data should be aggregated. It also specifies a list of metrics (the type of data) that will be aggregated from the regions of interest. 
  * Data File [-d]: The data file contains the raw metrics obtained from the simulation.
  * Ouput File [-o]: After the script has executed, the output file will display the aggregated metrics from the regions of interests that were both specified in the project file. The output file will be saved in the same folder as the script. 

Command Line Syntax: `python pydre_run.py -p [project file path] -d [data file path] -o [output file name]`

For additional assistance while running the script use the help command (-h)

# Project Files

Project files are JSON marked up files that dictate things like which region of interest should be tested and which metrics should be gathered. A project file should consist of two main parts: the rois array and the metrics array. Each element of the rois array should have a field to tell which type of roi the element is (rect or time) and a corresponding file name with a path to a csv file with the relevant information for a region. Time and Space are currently the only two roi types implemented. Their formats are detailed below. 

As for metrics, the array should consist of elements containing every function that you wish to analyze. There are a minimum of two required fields: name and function. Name is the column header for the metric in the output file and function is the name of the function you wish to call in pydre. Then, any arguments required for the function must be specified. 
    

# Region of Interest CSV File Formats

For analysis, it is often useful to define regions of interest in the data.  pydre uses csv files to define spatial and temporal regions of interest.
The spatial regions are defined over the scenario course, while the temporal regions are defined per subject.

#### Time ROI table format

| Subject | _roi name 1_  | _roi name 2_  | ... | _roi name N_  |
|---------|-----------|-----------|-----|-----------|
| 1 | _time range_ | _time range_ | ... | _time range_ |
| 2 | _time range_ | _time range_ | ... | _time range_ |
| ...     | ...       | ...       | ... | ... |
| N | _time range_ | _time range_ | ... | _time range_ |

*_NOTE_: Time Ranges are formatted as `hh:mm:ss-hh:mm:ss#driveID` If multiple drives are used in a praticular ROI, simply add a space and write in another time range in the same cell.*

#### Space ROI table format

| ROI    | X1 | Y1 | X2 | Y2 |
|--------|----|----|----|----|
|_ROI name_|_min x_|_min y_|_max x_|_max y_|
|_ROI name_|_min x_|_min y_|_max x_|_max y_|
|...       |...    |...    |...    |...    |
|_ROI name_|_min x_|_min y_|_max x_|_max y_|
  
# pydre/core.py

This script contains code that is intergral to the pydre module

### DriveData

This is the unit of data storage for the module. Each DriveData object contains a singular SubjectID, a list of DriveIDs, a single (optional) region of interest, a list of Pandas DataFrames created from the associated.dat files, and a list of the source file names. 

  - SubjectID: Is a unique identifier for this object. Any file loaded into a DriveData object should ONLY be data from this subject number, however, this is not currently enforced.
  - DriveID: Is a list of all of the drive ids for each DataFrame in the DriveData object.
  - roi: Is a singular string denoting the region of interest of the particular DriveData. There can currently only be one region of interest per DriveData object
  - data: A list of the DataFrames corresponding to each drive from the DriveIDs
  - sourcefilename: The names of each source file used in the data argument.
  
### `SliceByTime()`

This is a simple helper method to take a particular data frame and trim it to only entries that fall within a given range of times.

### `MergeBySpace()`

This is a utility to merge an ordered list of DriveData objects based on the point where the beginning of the next is closest (by X,Y position) to the end of the most previous DataFrame. The input should all be from the same subject, same region of interest, and should go in a logical order. The output will be a DriveData object with one element in the data list. The drive IDs and source file names of the outputted DriveData object will simply be an aggregation of all drive IDs and source files from the input list.

# pydre/project.py

This is where the processing actually takes place. The only functions that should be called outside of the project.py class are `__init(projectfilename)__`, `run(datafiles)`, and `save(outfilename)`. The basic idea is that init will load the json projectfile, run will convert all of the datafiles into DriveData objects and do all of the processing specified in the json file, and save will wrtie all of the results to a csav file. For further details, investigate the project.py script.

# pydre/rois.py

Contains functions to read ROI csv files referenced by the project file. These functions take that ROI data and a list of drive data objects, extract the data that falls within the region, and return a new list of DriveData objects with only the pertinent information.

### `TimeROI.__init__(filename, nameprefix="")`

Creates a new Time ROI object. filename is the file containing the rois.

### `TimeROI.split(datalist)`

Grabs relevant parts of a list of DriveData objects based on the filename used to create the object.

### `SpaceROI.__init__(filename, nameprefix="")`

Creates a new Space ROI object. filename is the file containing the rois.

### `SpaceROI.split(datalist)`

Grabs relevant parts of a list of DriveData objects based on the filename used to create the object.

# pydre/metrics.py

Contains all functions for getting data metrics out of the DraveData DataFrames. The functions that are defined in the json projectfile are called from during project.py's run function.  Each metric takes in a DriveData obejct, processes it, and returns the value of the metric. Currently, the following functions are implemented (with additional arguments described beneath):

  - `meanVelocity(data, cutoff)` 
    - data: the DriveData to be analyzed.
    - cutoff: the minimum velocity to be counted in the average
  - `steeringEntropy(data)`
    - data: the DriveData to be analyzed.
  - `tailgatingTime(data, cutoff = 2)`
    - data: the DriveData to be analyzed.
    - cutoff: The largest value of headway time (in seconds) that counts as tailgating.
  - `tailgatingPercentage(data, cutoff = 2)`
    - data: the DriveData to be analyzed.
    - cutoff: The largest value of headway time (in seconds) that counts as tailgating.
  - `brakeJerk(data, cutoff = 0)`
    - data: the DriveData to be analyzed.
    - cutoff: Smallest amount of jerk to be counted

