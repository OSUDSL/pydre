# Pydre documentation

## pydre_run.py

Pydre is software used to analyze data collected from studies. When experiments are run in the simulator, the program SimObserver collects information on the drive, such as vehicle speed and following distance. This information is gathered every 1/60th of a second, which results in many data points. These data points can be analyzed by examining trends over longer periods of time, and this is done through Pydre. Pydre takes a file with data that is difficult to interpret in the form it comes in and then converts it into a much more comprehensive format (i.e. Excel). 

This script is a front end application that allows the user to analyze data using command line arguments.

The user must enter the path for the project file and data file in order to aggregate the data. The user has the option of specifying an output file name, to which the test results will be saved. If no output file name is given the output will save to _"out.csv"_ by default. A brief description of the aforementioned arguments is offered below.

Command Line Arguments:

  * Project File [-p]: The project file specifies a file for the regions of interest from which the data should be aggregated. It also specifies a list of metrics (the type of data) that will be aggregated from the regions of interest. 
  * Data File [-d]: The data file contains the raw metrics obtained from the simulation.
  * Ouput File [-o]: After the script has executed, the output file will display the aggregated metrics from the regions of interests that were both specified in the project file. The output file will be saved in the same folder as the script. 
  * Logger level [-l]: This defines the level the logger will print out. The dafault is 'Warning'. Options include debug, info, warning, error, and critical.
  
Command Line Syntax: `python pydre_run.py -p [project file path] -d [data file path] -o [output file name] -l [warning level]`

Example execution: 
'python pydre_run.py -p C:\Users\pveith\Documents\pydre\docs\bioptics.json -d C:\Users\pveith\Documents\bioptics\pydreDataSet\*.dat -o bioptics.csv -l debug'

For additional assistance while running the script use the help command (-h)



## Project Files

Project files are JavaScript Object Notation (json) marked-up files that dictate things like which region of interest (ROI) should be tested and which metrics should be gathered. A project file should consist of two main parts: the rois array and the metrics array. Each element of the rois array should have a field to tell which type of ROI the element is (rect or time) and a corresponding file name with a path to a csv file with the relevant information for a region. Time and Space are currently the only two ROI types implemented. Their formats are detailed below. 

As for metrics, the array should consist of elements containing every function that you wish to analyze. There are a minimum of two required fields: "name" and "function". "Name" is the column header for the metric in the output file and "function" is the name of the function you wish to call in Pydre. Then, any arguments required for the function must be specified. 

Multiple functions can be called within one project file.  The result of each function will be outputted in a separate column of the generated csv file.

To see an example project file, look at bushman_pf.json in the docs directory of the pydre folder.    


  
# pydre/core.py

This script contains code that is intergral to the pydre module

### DriveData

This is the unit of data storage for the module. Each DriveData object contains a singular SubjectID, a list of DriveIDs, a single (optional) region of interest, a list of Pandas DataFrames created from the associated.dat files, and a list of the source file names. 

  - SubjectID: Unique identifier for this object. Any file loaded into a DriveData object should ONLY be data from this subject number, however, this is not currently enforced
  - DriveID: List of all of the drive ids for each DataFrame in the DriveData object
  - roi: Singular string denoting the region of interest of the particular DriveData. There can currently only be one region of interest per DriveData object
  - data: List of the DataFrames corresponding to each drive from the DriveIDs
  - sourcefilename: The names of each source file used in the data argument
  
### `SliceByTime()`

This is a simple helper method to take a particular data frame and trim it to only entries that fall within a given range of times.

### `MergeBySpace()`

This is a utility to merge an ordered list of DriveData objects based on the point where the beginning of the next is closest (by X,Y position) to the end of the most previous DataFrame. The input should all be from the same subject, same region of interest, and should go in a logical order. The output will be a DriveData object with one element in the data list. The drive IDs and source file names of the outputted DriveData object will simply be an aggregation of all drive IDs and source files from the input list.

# pydre/project.py

This is where the processing actually takes place. The only functions that should be called outside of the project.py class are `__init(projectfilename)__`, `run(datafiles)`, and `save(outfilename)`. The basic idea is that "init" will load the json projectfile, "run" will convert all of the datafiles into DriveData objects and do all of the processing specified in the json file, and "save" will write all of the results to a csv file. For further details, investigate the project.py script.

