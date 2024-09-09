---
title: Project Files
---

# Project Files

Project files define the processing steps applied to the dataset. This is how users of the software specify the filters, regions of interest, and metrics that are run to get the final processed CSV output.

Project files can be written in [TOML](https://toml.io/) or [JSON](https://www.json.org/) [^1]. We recommend using TOML project files for ease of writing, but anything you can do in one format, you can do with the other. 

# Anatomy of a project file

```toml title="test1_pf.toml"

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

Project files have three types of elements: filters, ROIs and metrics. In the TOML file, the start of each element is in the format `[elementtype.elementname]` where *elementtype* is one of "filters", "rois", or "metrics" and *elementname* is the name of the element. Names must be unique between elements of the same type. For filters and ROIs, the names are just for reference, but for the metrics, the name of the element defines the name of the output column where the metric results are placed. 

Below the start of each element, fields for the element are defined. Filters and metrics both have a mandatory *function* field. This field is the [metric function](../reference/metrics.md) or [filter function](../reference/filters.md) that is called internally during data processing. Each filter or metric has additional fields that may or must be defined to run correctly. 

[ROIs](../explanation/rois.md) can also be defined, and aid in computing repeated measures experiments or in any experiments where it is useful to partition each datafile into different parts before metrics are run. 

[^1]: JSON was the first format used for project files, but we recommend moving to TOML. If additional functions are added to project files, they may be added to the TOML format only. 