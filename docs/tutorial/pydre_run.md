# Getting Started

Pydre is a python application, run from the command line. The recommended way to set up your local 
environment to run Pydre is to use [Rye](https://rye.astral.sh/):

1. Install Rye.
2. Either clone the Git repository to a local directory or unzip a release package of Pydre
3. Navigate to the Pydre directory in the terminal.
4. Run `rye sync`

This will download the appropriate python packages needed to run Pydre.

# pydre_run.py

This script is a front end application that allows the user to analyze data using command line arguments.

The user must enter the path for the project file and data file in order to aggregate the data. The user has the option of specifying an output file name, to which the test results will be saved. If no output file name is given the output will save to _"out.csv"_ by default. A brief description of the aforementioned arguments is offered below.

Command Line Arguments:

  * Project File [-p]: The project file specifies a file for the regions of interest from which the data should be aggregated. It also specifies a list of metrics (the type of data) that will be aggregated from the regions of interest. 
  * Data File [-d]: The data file contains the raw metrics obtained from the simulation. This argument supports wildcards.
  * Output File [-o]: After the script has executed, the output file will display the aggregated metrics from the regions of interests that were both specified in the project file. The output file will be saved in the same folder as the script. 
  * Logger level [-l]: This defines the level the logger will print out. The default is 'warning'. Options include debug, info, warning, error, and critical.
  
Command Line Syntax: 
```
python pydre_run.py -p [project file path] -d [data file path] 
    -o [output file name] -l [warning level]
```

Example execution: 
```
python pydre_run.py -p C:\Users\pveith\Documents\pydre\docs\bioptics.json 
    -d C:\Users\pveith\Documents\bioptics\pydreDataSet\*.dat 
    -o bioptics.csv -l debug
```
