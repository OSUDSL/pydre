# Developer notes

If you want to create your own metrics or filters, we recommend
setting up a local development environment. 

The recommended way to set up your local 
environment to run Pydre is to use [Rye](https://rye.astral.sh/):

1. Install Rye.
2. Either clone the Git repository to a local directory or unzip a release package of Pydre
3. Navigate to the Pydre directory in the terminal.
4. Run `rye sync`

This will download the appropriate python packages needed to run Pydre.



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

