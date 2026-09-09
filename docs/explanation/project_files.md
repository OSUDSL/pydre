---
title: Project Files
---

# Project Files

Project files define the processing steps applied to the dataset. This is how users of the software specify the filters, regions of interest, and metrics that are run to get the final processed CSV output. Project files are written in [TOML](https://toml.io/).

# Anatomy of a project file

```toml title="test1_pf.toml"
[config]
outputfile = "Anasazi_output.csv"
datafiles = ["E:/work/data/Anasazi/*.dat"]

[filters.XPos_zscore]
function = "zscoreCol"
col = "Velocity"
newcol = "Velocity_zscore"

[rois.CruiseButtons]
type = "column"
columnname = "CruiseButtons"

[metrics.meanZscoreVel]
function = "colMean"
var = "Velocity_zscore"

[metrics.meanYPos]
function = "colMean"
var = "YPos"
```

Project files have four types of elements: config, filters, ROIs and metrics. For the latter three, In the TOML file, the start of each element is in the format `[elementtype.elementname]` where *elementtype* is one of "filters", "rois", or "metrics" and *elementname* is the name of the element. Names must be unique between elements of the same type. For filters and ROIs, the names are just for reference, but for the metrics, the name of the element defines the name of the output column where the metric results are placed. 

Below the start of each element, fields for the element are defined. Filters and metrics both have a mandatory *function* field. This field is the [metric function](../reference/metrics.md) or [filter function](../reference/filters.md) that is called internally during data processing. Each filter or metric has additional fields that may or must be defined to run correctly. 

[ROIs](../explanation/rois.md) can also be defined, and aid in computing repeated measures experiments or in any experiments where it is useful to partition each datafile into different parts before metrics are run. 

## Config Section

The `config` section of the project file is used to define global variables that are used during processing. The available configuration options are:

* `source`: Determines where data files are loaded from. Currently, `localfilesystem` and `ducklake` are supported. 
* `baseDirectory`: Specifies the directory containing the data files when `source` is `localfilesystem`. 
* `project` : Specifies the project name used to select files when the `source` is `ducklake`. 
* `pattern`: A regular expression used to select files from the specified source. 
* `datafiles`: Explicitly specifies a list of data files to process. 
* `ignore`: Specifies a list of files to exclude from processing. 
* `datafile_type`: Specifies the format of the input data. Currently, `rti`, `oldrti`, and `scanner` are supported. Defaults to `rti`.
* `logfile`: Specifies the file where logged messages can be recorded and saved. Defaults to `None`. 
* `log_level`: The minimum severity level from which logged messages should be sent to the sink. Defaults to `WARNING`
* `outputfile`: Specifies the file where the aggregated metrics are written. Defaults to `out.csv`.
* `num_threads`: Number of threads to run simultaneously in the thread pool.
* `infer_schema_length`: The maximum number of rows to scan for schema inference.
* `custom_metrics_dirs`: Specifies a list of directory paths for custom metrics. 
* `custom_filters_dirs`: Specifies a list of directory paths for custom filter.

For more information about using the local file system as a data source, see [Using Local Files](../tutorial/using_local_files.md). For more information about using DuckLake as a data source, see [Using DuckLake](../tutorial/using_ducklake.md)






