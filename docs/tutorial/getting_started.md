# Getting Started

Pydre is a Python application, run from the command line. 

# pydre.run

The main entry point to run Pydre is `pydre.run`. This application that allows the user to analyze data using command line arguments.

The user must enter the path for the project file and data file in order to aggregate the data. The user has the option of specifying an output file name, to which the test results will be saved. If no output file name is given the output will save to _"out.csv"_ by default. A brief description of the aforementioned arguments is offered below.

!!! info "Command Line Arguments for `pydre.run`"
    * Project File [-p]: The project file specifies a file for the regions of interest from which the data should be aggregated. It also specifies a list of metrics (the type of data) that will be aggregated from the regions of interest. 

    * Data File [-d]: The data file contains the raw metrics obtained from the simulation. This argument supports wildcards.
    
    * Output File [-o]: After the script has executed, the output file will display the aggregated metrics from the regions of interests that were both specified in the project file. The output file will be saved in the same folder as the script. 
    
    * Logger level [-l]: This defines the level the logger will print out. The default is 'warning'. Options include debug, info, warning, error, and critical.
  
Command Line Syntax: 
```
python -m pydre.run -p [project file path] -d [data file path] 
    -o [output file name] -l [warning level]
```

Example execution: 
```
python -m pydre.run -p C:\Users\pveith\Documents\pydre\docs\bioptics.json 
    -d C:\Users\pveith\Documents\bioptics\pydreDataSet\*.dat 
    -o bioptics.csv -l debug
```

# Example data processing

