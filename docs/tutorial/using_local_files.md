---
title: Using Local Files
---

# Using Local Files

pydre can load data files from the local file system.

To use the local file system as the data source, set the `source` option to `localfilesystem` in the project file:

```toml
[config]
source = "localfilesystem"
```

When using local file system, at least one of  `datafiles`  or a `baseDirectory` and `pattern` must be specified to select the data files to process.

## Using `datafiles`

The `datafiles` option can be used to explicitly specify the files to process:

```toml
[config]
source = "localfilesystem"
datafiles = ["E:/work/data/Anasazi/file1.dat", "E:/work/data/Anasazi/file2.dat"]
```

## Using `baseDirectory` and `pattern`

The `baseDirectory` specifies the directory containing the data files, while `pattern` is a regular expression to select the files to process: 

```toml
[config]
source = "localfilesystem"
baseDirectory = "E:/work/data/Anasazi"
pattern = ".dat$"
```




