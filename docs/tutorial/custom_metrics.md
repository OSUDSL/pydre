---
title: "Writing Custom Metrics for Pydre"
---

Pydre ships with a library of built-in metric functions. When those don't cover your needs, you can write your own. Custom metrics in Pydre allow you to extract meaningful data from driving simulation data. Here's how to create one:

## Basic Metric Structure

A custom metric is a function decorated with `@registerMetric()` that takes a `DriveData` object as its first parameter and returns a numeric value or collection of values.

---

## Step-by-step guide
 
### 1. Create a custom metrics directory
 
Add a directory for your custom metrics inside your project:
 
```
my_project/
├── custom_metrics/
│   └── custom.py
├── data/
│   └── drive_data.dat
└── my_project.toml
```
 
### 2. Write your custom metric
 
Create a Python file in the directory. Each metric is a function decorated with `@registerMetric()` that takes a `DriveData` object as its first parameter and returns a numeric value (or a list of values for multi-column metrics).

```python title="custom_metric/custom.py"
from typing import Optional

import polars as pl
import pydre.core
from pydre.core import ColumnsMatchError
from pydre.metrics import registerMetric
from loguru import logger

@registerMetric()
def testMean(
    drivedata: pydre.core.DriveData, var: str, cutoff: Optional[float] = None
) -> Optional[float]:
    """Mean of a column, optionally filtered to values above a cutoff.
 
    Parameters:
        var: Name of the column to average.
        cutoff: If provided, only values >= cutoff are included.
 
    Note: Requires data columns
        - var: must be numeric
 
    Returns:
        Mean of the (filtered) column, or None if the column is non-numeric.
    """
    try:
        drivedata.checkColumnsNumeric([var])
    except ColumnsMatchError:
        logger.warning(f"testMean: column '{var}' is not numeric, returning None")
        return None
 
    if cutoff is not None:
        return (
            drivedata.data.get_column(var)
            .filter(drivedata.data.get_column(var) >= cutoff)
            .mean()
        )
    else:
        return drivedata.data.get_column(var).mean()

```

**Best Practices:**

1. Always validate required columns exist before processing
2. Use robust error handling with clear log messages
3. Return `None` when calculation fails rather than raising exceptions
4. Include comprehensive docstrings with parameter descriptions
5. Use polars operations when possible for performance

### 4. Configure Your Project File

Include your custom metrics directory in the config section of your [project file](../explanation/project_files.md). 

```toml title="custom_test.toml"
[config]
custom_metrics_dirs = ["custom_metric"]

[metrics.custom_test]
function = "testMean"
var = "XPos"

```

### 5. Run Pydre with Your Custom Metrics

[Run Pydre](../explanation/execution.md) with your project file:

```bash
uv run pydre -p examples/custom_project/custom_test.toml -d examples/custom_project/data/Experimenter_S1_Tutorial_11002233.dat -o custom.csv
```

## How It Works

1. Pydre loads all metrics defined in its core library
2. It then searches the directory paths specified in `custom_metrics_dirs`
3. For each Python file in those directories, it dynamically imports the metrics
4. The `@registerMetric()` decorator automatically registers your custom metrics with *pydre*
5. Your metrics become available for use in the project configuration

## Tips

- Ensure your custom metrics follow the same pattern as built-in metrics
- Add proper docstrings to document required columns and return values
- Always include error handling for missing columns using `checkColumns` or `checkColumnsNumeric`
- Use type hints to document your function parameters and return values

With this approach, you can maintain your custom metrics separately from the Pydre codebase while still using them in your projects.

---

## Advanced Metrics

### Multiple Return Values

For metrics that return multiple values, specify column names in the decorator:

```python
@registerMetric(columnnames=["value1", "value2"])
def multiValueMetric(drivedata: pydre.core.DriveData) -> list[float]:
    # ...
    return [value1, value2]
```

### Custom Metric Names

Override the function name for metric registration:

```python
@registerMetric(metricname="betterMetricName")
def internal_function_name(drivedata: pydre.core.DriveData) -> float:
    # ...
```

---

# Custom filters

Custom filters can be created in a similar way to custom metrics. the search path for custom filters is similar to the custom metrics search path: "custom_filters_dirs". Additionally, `@registerFilter()` instead of `@registerMetric()` is used as the decorator.

## Example

```toml 
[config]
datafiles = ["data/drive_data.dat"]
outputfile = "results.csv"
custom_metrics_dirs = ["custom_metrics"]
custom_filters_dirs = ["custom_filters"]
```

---

**Next:** [Setting up Just](justSetup.md)