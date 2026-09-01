---
title: Using DuckLake
---

# Using DuckLake

pydre can load data from DuckLake in addition to loading data from the local file system.

To use DuckLake as the data source, set the `source` option to `ducklake` in the project file:

```toml
[config]
source = "ducklake"
```

The DuckLake connection is configured using the `.env` file described in [Setting up Configuration File](settingUpConfigurationFile.md)

When using DuckLake, at least one of `datafiles`, `project`, or `pattern` must be specified to select the data files to process.

## Using `datafiles`

The `datafiles` option can be used to explicitly specify the files to process:

```toml
[config]
source = "ducklake"
datafiles = ["file1.dat", "file2.dat"]
```

## Using `pattern`

The `pattern` option can be used to select files using a regular expression. 

```toml
[config]
source = "ducklake"
pattern = ".dat$"
```

## Using `project`

The project option can be used to select files associated with a specific project. 

```toml
[config]
source = "ducklake"
project = "Anasazi"
```


