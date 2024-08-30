# Pydre

Pydre is software used to analyze data collected from studies. When experiments are run in the simulator, the program SimObserver collects information on the drive, such as vehicle speed and following distance. This information is gathered every 1/60th of a second, which results in many data points. These data points can be analyzed by examining trends over longer periods of time, and this is done through Pydre. Pydre takes a file with data that is difficult to interpret in the form it comes in and then converts it into a much more comprehensive format (i.e. Excel).

# pydre_run.py

This script is a front end application that allows the user to analyze data using command line arguments.

The user must enter the path for the project file and data file in order to aggregate the data. The user has the option of specifying an output file name, to which the test results will be saved. If no output file name is given the output will save to _"out.csv"_ by default. A brief description of the aforementioned arguments is offered below.

Command Line Arguments:

-   Project File [-p]: The project file specifies a file for the regions of interest from which the data should be aggregated. It also specifies a list of metrics (the type of data) that will be aggregated from the regions of interest.
-   Data File [-d]: The data file contains the raw metrics obtained from the simulation.
-   Ouput File [-o]: After the script has executed, the output file will display the aggregated metrics from the regions of interests that were both specified in the project file. The output file will be saved in the same folder as the script.
-   Logger level [-l]: This defines the level the logger will print out. The dafault is 'Warning'. Options include debug, info, warning, error, and critical.

Command Line Syntax: `python pydre_run.py -p [project file path] -d [data file path] -o [output file name] -l [warning level]`

Example execution:
'python pydre_run.py -p C:\Users\pveith\Documents\pydre\docs\bioptics.json -d C:\Users\pveith\Documents\bioptics\pydreDataSet\*.dat -o bioptics.csv -l debug'

For additional assistance while running the script use the help command (-h)

# Regions of Interest (ROIs)

Each region of interest is an area of data that the user is interested in examining. This can include things such as where the car starts on the track, when the car hits a traffic jam, when the car hits construction, etc.

# Project Files

Project files define what filters, region of interest (ROI) divisions, and metrics are applied to the datafiles.

# ROI CSV File Formats

For analysis, it is often useful to define ROIs in the data. Pydre uses csv files to define spatial and temporal ROIs.
The spatial regions are defined over the scenario course, while the temporal regions are defined per subject.

#### Time ROI table format

| Subject | _ROI name 1_ | _ROI name 2_ | ... | _ROI name N_ |
| ------- | ------------ | ------------ | --- | ------------ |
| 1       | _time range_ | _time range_ | ... | _time range_ |
| 2       | _time range_ | _time range_ | ... | _time range_ |
| ...     | ...          | ...          | ... | ...          |
| N       | _time range_ | _time range_ | ... | _time range_ |

_*NOTE*: Time Ranges are formatted as `hh:mm:ss-hh:mm:ss#driveID` If multiple drives are used in a particular ROI, simply add a space and write in another time range in the same cell._

#### Space ROI table format

| ROI        | X1      | Y1      | X2      | Y2      |
| ---------- | ------- | ------- | ------- | ------- |
| _ROI name_ | _min x_ | _min y_ | _max x_ | _max y_ |
| _ROI name_ | _min x_ | _min y_ | _max x_ | _max y_ |
| ...        | ...     | ...     | ...     | ...     |
| _ROI name_ | _min x_ | _min y_ | _max x_ | _max y_ |

Note: -Z corresponds to positive X, and if Y is 0 in the WRL file, set Y1 = -100, Y2 = 100.

The ROI will consist of the area inside the max_y - min_y and the max_x - min_x.

For an example file, look at spatial_rois.csv in the main pydre folder. Once the ROI csv file has been generated, reference it in the project file (as seen in bushman_pf.json) to perform the function calculations only on the regions of interest specified by the x and y coordinates in this csv file.
