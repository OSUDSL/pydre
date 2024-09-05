# Regions of Interest (ROIs)
Each region of interest is an area of data that the user is interested in examining. This can include things such as where the car starts on the track, when the car hits a traffic jam, when the car hits construction, etc. 

# Time ROI

# Space ROI

# Column ROI



## ROI CSV File Formats

For analysis, it is often useful to define ROIs in the data.  Pydre uses csv files to define spatial and temporal ROIs.
The spatial regions are defined over the scenario course, while the temporal regions are defined per subject.

#### Time ROI table format

| Subject | _ROI name 1_ | _ROI name 2_ | ... | _ROI name N_ |
|---------|--------------|--------------|-----|--------------|
| 1       | _time range_ | _time range_ | ... | _time range_ |
| 2       | _time range_ | _time range_ | ... | _time range_ |
| ...     | ...          | ...          | ... | ...          |
| N       | _time range_ | _time range_ | ... | _time range_ |

*_NOTE_: Time Ranges are formatted as `hh:mm:ss-hh:mm:ss#driveID` If multiple drives are used in a particular ROI, simply add a space and write in another time range in the same cell.*

#### Space ROI table format

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

