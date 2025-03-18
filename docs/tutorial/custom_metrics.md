# Writing Custom Metrics for Pydre

Custom metrics in Pydre allow you to extract meaningful data from driving simulation data. Here's how to create one:

## Basic Metric Structure

A custom metric is a function decorated with `@registerMetric()` that takes a `DriveData` object as its first parameter and returns a numeric value or collection of values.

```python
from pydre.metrics import registerMetric
import pydre.core

@registerMetric()
def myCustomMetric(drivedata: pydre.core.DriveData, param1: str = "default") -> float:
    """Brief description of what this metric calculates
    
    Parameters:
        param1: Description of this parameter
        
    Note: Requires data columns
        - Column1: Description of required column
        - Column2: Description of another required column
        
    Returns:
        Description of return value
    """
    # Check for required columns
    required_cols = ["Column1", "Column2"]
    drivedata.checkColumns(required_cols)
    
    # Verify columns are numeric
    try:
        drivedata.checkColumnsNumeric(required_cols)
    except pydre.core.ColumnsMatchError:
        return None
        
    # Process data and compute the metric value
    result = some_calculation(drivedata.data)
    
    return result
```

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

## Best Practices

1. Always validate required columns exist before processing
2. Use robust error handling with clear log messages
3. Return `None` when calculation fails rather than raising exceptions
4. Include comprehensive docstrings with parameter descriptions
5. Use polars operations when possible for performance

## Step-by-Step Guide

### 1. Create a Custom Metrics Directory

Create a directory for your custom metrics outside the Pydre repository:

```
my_project/
├── custom_metrics/
│   └── my_metrics.py
├── data/
│   └── drive_data.dat
└── project_config.toml
```

### 2. Write Your Custom Metrics

Create a Python file (e.g., `my_metrics.py`) in your custom metrics directory. Your metrics should use the `@registerMetric()` decorator:

```python
from pydre.metrics import registerMetric
import polars as pl
from typing import Optional
import pydre.core

@registerMetric()
def averageSpeed(drivedata: pydre.core.DriveData) -> Optional[float]:
    """Calculate the average speed during the drive
    
    Note: Requires data columns
        - Velocity: Speed in meters per second
    
    Returns:
        Average velocity in meters per second
    """
    try:
        drivedata.checkColumnsNumeric(["Velocity"])
    except Exception:
        return None
        
    return drivedata.data.select(pl.col("Velocity").mean()).item()
```

### 3. Configure Your Project File

Update your project configuration file to include the custom metrics directory. This direc

```toml
[config]
datafiles = ["data/drive_data.dat"]
outputfile = "results.csv"
custom_metrics_dirs = ["custom_metrics"]

[[metrics]]
name = "avg_speed"
function = "averageSpeed"

[[rois]]
name = "full_drive"
type = "time"
filename = "data/drive_times.csv"
```

### 4. Run PyDRE with Your Custom Metrics

Run PyDRE with your project file:

```bash
pydre -p project_config.toml
```

## How It Works

1. Pydre loads all metrics defined in its core library
2. It then searches the directory paths specified in `custom_metrics_dirs`
3. For each Python file in those directories, it dynamically imports the metrics
4. The `@registerMetric()` decorator automatically registers your custom metrics with PyDRE
5. Your metrics become available for use in the project configuration

## Tips

- Ensure your custom metrics follow the same pattern as built-in metrics
- Add proper docstrings to document required columns and return values
- Always include error handling for missing columns using `checkColumns` or `checkColumnsNumeric`
- Use type hints to document your function parameters and return values

With this approach, you can maintain your custom metrics separately from the Pydre codebase while still using them in your projects.
