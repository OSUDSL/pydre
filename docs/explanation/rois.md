# Regions of Interest (ROIs)
Each region of interest is an area of data that the user is interested in examining. This can include things such as where the car starts on the track, when the car hits a traffic jam, when the car hits construction, etc. 

Pydre uses csv files to define three types of ROIS: temporal, spatial, and rectangular.


# Time ROI
Time ROIs are used to define groups of data according to given time ranges. Any of the three time data columns can be
used: DatTime, SimTime, or MediaTime. If no column name is given, then DatTime is used by default. 

The Time ROI file `.csv` is formatted as below:

| ROI          | time_start     | time_end     | 
|--------------|----------------|--------------|
| _ROI name 1_ | _start time 1_ | _end time 1_ | 
| _ROI name 2_ | _start time 2_ | _end time 2_ |
| ...          | ...            | ...          | 
| _ROI name N_ | _start time N_ | _end time N_ |

!!! note
    Start and end times are formatted as either `hh:mm:ss-hh:mm:ss` or `mm:ss-mm:ss`.


# Space ROI


| ROI        | X1      | Y1      | X2      | Y2      |
|------------|---------|---------|---------|---------|
| _ROI name_ | _min x_ | _min y_ | _max x_ | _max y_ |
| _ROI name_ | _min x_ | _min y_ | _max x_ | _max y_ |
| ...        | ...     | ...     | ...     | ...     |
| _ROI name_ | _min x_ | _min y_ | _max x_ | _max y_ |
  

!!! note
    -Z corresponds to positive X, and if Y is 0 in the WRL file, set Y1 = -100, Y2 = 100.
  
The ROI will consist of the area inside the max_y - min_y and the max_x - min_x.
  
For an example file, look at spatial_rois.csv in the main pydre folder.  Once the ROI csv file has been generated, reference it in the project file (as seen in bushman_pf.json) to perform the function calculations only on the regions of interest specified by the x and y coordinates in this csv file.



# Column ROI
