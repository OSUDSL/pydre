# Developer notes

## Development environment

If you want to create your own metrics or filters, we recommend
setting up a local development environment. 

The recommended way to set up your local 
environment to run Pydre is to use [Rye](https://rye.astral.sh/):

1. Install Rye.
2. Either clone the Git repository to a local directory or unzip a release package of Pydre
3. Navigate to the Pydre directory in the terminal.
4. Run `rye sync`

This will download the appropriate python packages needed to run Pydre.

## DriveData objects

This is the primary unit of data storage for the module. DriveData objects are initially created from dat files, and then they are split by the ROI functions. 

  - SubjectID: Unique identifier for this object. Any file loaded into a DriveData object should ONLY be data from this subject number, however, this is not currently enforced
  - roi: Singular string denoting the region of interest of the particular DriveData. There can currently only be one region of interest per DriveData object
  - data: Polars dataframe containing the rows of the drive data
  - sourcefilename: The filename of where the data originally came from
  

# Project objects

This is where the processing actually takes place. A project is constructed by reading in a project file (either JSON or TOML). 


