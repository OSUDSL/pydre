# Basic Analysis
 
Pydre is a Python application run from the command line. This guide walks you through creating your first project file and running it on example data to produce your first aggregated metrics output.
 
---
 
## Command Line Syntax
 
The basic command syntax is:
 
```
uv run pydre -p [project file] -d [data file] -o [output file] -l [log level]
```

!!! info "Command Line Arguments for `pydre`"

    * Project File [-p]: The project file specifies a file for the regions of interest from which the data should be aggregated. It also specifies a list of metrics (the type of data) that will be aggregated from the regions of interest. 

    * Data File [-d]: The data file contains the raw metrics obtained from the simulation. This argument supports wildcards.
    
    * Output File [-o]: After the script has executed, the output file will display the aggregated metrics from the regions of interests that were both specified in the project file. The output file will be saved in the same folder as the script. 
    
    * Logger level [-l]: This defines the level the logger will print out. The default is 'warning'. Options include debug, info, warning, error, and critical.

---

## Your First Project File

Project files are written in TOML. Each metric is defined as a section with a function name and any parameters that function requires. Here's a minimal example that calculates the standard deviation of lane position (SDLP):

```toml
[metrics.SDLP]
function = "colSD"
var = "LaneOffset"
```

The section name `metrics.SDLP` tells Pydre this is a metric called `SDLP`. The `function` field refers to a built-in Pydre function, and `var` specifies which column in the data file to operate on.

---

## Running on Example Data

Save the project file above as `tutorial.toml`, then run:

```
uv run pydre -p tutorial.toml -d Experimenter_S1_Tutorial_11002233.dat -o tutorial.csv
```

Pydre will process the data file and write the results to `tutorial.csv`. With no regions of interest defined, the output contains one row per input file:

| Subject | Mode | ScenarioName | UniqueID | ROI | SDLP |
|---|---|---|---|---|---|
| S1 | Experimenter | Tutorial | 11002233 | | 0.0456... |

The `ROI` column is blank because no regions of interest were specified. The `SDLP` column header matches the name given in the project file.

---

Once you're comfortable running basic analyses, move on to [Custom Metrics](custom_metrics.md) to learn how to write your own metric functions.