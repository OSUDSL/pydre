
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
  - `boxMetrics(data, cutoff = 0, stat = "count")`
    - data: the DriveData to be analyzed.
    - cutoff: Smallest amount of jerk to be counted
    - stat: statistic to compute, either "count" for the number of times the participant identified the box within 2 seconds, "mean" for their mean reaction time, or "sd" for the standard deviation of their reaction time. Used for Anna's hearing impaired study.

 