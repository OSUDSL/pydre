# pydre_run.py

This script is a front end application that allows the user to analyze data using command line arguments.

The user must enter the path for the project file and data file in order to aggregate the data. The user has the option of specifying an output file name, to which the test results will be saved. If no output file name is given the output will save to _"out.csv"_ by default. A brief description of the aforementioned arguments is offered below.

Command Line Arguments:
  - Project File [-p]: The project file contains the regions of interest from which the data should be aggregated. It also specifies a list of metrics (the type of data) that will be aggregated from the regions of interest. 
  - Data File [-d]: The data file contains the raw metrics obtained from the simulation.
  - Ouput File [-o]: After the script has executed, the output file will display the aggregated metrics from the regions of interests that were both specified in the project file. The output file will be saved in the same folder as the script. 

Command Line Syntax: _python pydre_run.py -p [project file path] -d [data file path] -o [output file name]_

For additional assistance while running the script use the help command: [-h] or [- -help] 
  