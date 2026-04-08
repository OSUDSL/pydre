---
title: "Using Just for a Pydre Project"
---

*Automating Pydre analysis runs with just and uv*

---

Pydre should always be invoked through `uv run just` rather than directly, to ensure the correct environment is used and outputs are consistent across runs. A justfile encodes your project's targets: which project files to use, where the data lives, and where results should go; so that running a full analysis is a single command.

---
 
## Prerequisites
 
Before continuing, ensure you have completed the previous steps in this tutorial:
 
- Pydre installed and working (`uv run pydre --help` succeeds) — see [Installation](installation.md)
- A working project file and at least one successful analysis run — see [Running Pydre](basic_analysis.md)
 
Additionally, install `just`:
 
- See [just.systems](https://just.systems/man/en/installation.html) for platform-specific instructions.
- After installing, verify with `just --version`.
 
---

## Project Structure

A typical Pydre project using `just` looks like this:

```
my_project/
├── justfile
├── .env
├── pyproject.toml
├── uv.lock
├── pydre-projects/
│   └── overallMetrics.toml
└── out/
```


| File / Directory | Purpose |
|------------------|---------|
| `justfile` | Defines analysis targets and how to run them |
| `.env` | Stores the local path to raw data files (never committed to version control) |
| `pyproject.toml` | Python project configuration; lists pydre as a dependency |
| `uv.lock` | Locked dependency versions for reproducible installs |
| `pydre-projects/` | TOML project files defining filters, ROIs, and metrics |
| `out/` | Output directory where aggregated results are written |

---

## Step 1 — Create the .env File

The justfile reads the location of your raw simulator data from a local `.env` file. This keeps machine-specific paths out of the justfile itself, so the justfile can be shared across team members and committed to version control.

Create a file named `.env` in your project root:

```sh
# .env
rawdatadir="E:/Work/data/cleanData/"
```

The path should point to the directory containing your raw `.dat` simulator output files.

---

## Step 2 — Create the Justfile

Create a file named `justfile` (no extension) in your project root:

```just
# Shell configuration
set windows-shell := ["powershell.exe", "-c"]
set shell := ["zsh", "-c"]

# Load variables from .env automatically
set dotenv-load

# Build file patterns from the rawdatadir env variable
allDatFiles  := env('rawdatadir') / "*.dat"
testDatFiles := env('rawdatadir') / "*Test Drive*.dat"

# Default target — running `uv run just` with no arguments runs this
outfiles: overallMetrics

# Named analysis target
overallMetrics: (pydre-run "pydre-projects/overallMetrics.toml" "out/Metrics_Overall.csv" testDatFiles)

# Reusable recipe: runs pydre with given project file, output, and data glob
pydre-run PROJFILE OUTFILE DATFILES:
    uv run pydre -p '{{PROJFILE}}' -o '{{OUTFILE}}' -d '{{DATFILES}}'
```

> **Note:** The indentation before `uv run pydre` must be a real tab character, not spaces. Most editors will insert spaces by default — check your editor's settings if you see an indentation error.
 
> **macOS users:** If you use zsh as your default shell, change `"bash"` to `"zsh"` in the `set shell` line.

---

## Step 3 — Running the Analysis

**Run the default target** (everything `outfiles` depends on):

```sh
uv run just
```

**Run a specific target:**

```sh
uv run just overallMetrics
```

**List all available targets:**

```sh
uv run just --list
```

---

## Understanding the Justfile

### Shell Configuration

```just
set windows-shell := ["powershell.exe", "-c"]
set shell := ["zsh", "-c"]
```

These two lines tell `just` which shell to use when executing recipes. `windows-shell` is used on Windows; `shell` is used on macOS and Linux. Having both means the same justfile works on all platforms without modification.

### Loading Environment Variables

```just
set dotenv-load
```

This directive tells `just` to automatically read `.env` before running any recipe. Once loaded, variables like `rawdatadir` become available to the justfile via the `env()` function.

### Building File Path Patterns

```just
allDatFiles  := env('rawdatadir') / "*.dat"
testDatFiles := env('rawdatadir') / "*Test Drive*.dat"
```

These lines create variables by joining `rawdatadir` with a file pattern using the `/` path-join operator. The result is a full pattern like `E:/Work/data/cleanData/*.dat` that pydre uses to find input files.

| Variable | Matches |
|----------|---------|
| `allDatFiles` | All `.dat` files in `rawdatadir` |
| `testDatFiles` | Only files with `"Test Drive"` in the filename |

### Targets and Dependencies

```just
outfiles: overallMetrics

overallMetrics: (pydre-run "pydre-projects/overallMetrics.toml" "out/Metrics_Overall.csv" testDatFiles)
```

The `outfiles` target is the default. It runs when you call `uv run just` with no arguments. It depends on `overallMetrics`, which in turn calls the `pydre-run` recipe with specific arguments.

Chaining targets this way lets you build up complex multi-step pipelines. Adding a new analysis is as simple as adding a new target and listing it as a dependency of the default.

### The pydre-run Recipe

```just
pydre-run PROJFILE OUTFILE DATFILES:
    uv run pydre -p '{{PROJFILE}}' -o '{{OUTFILE}}' -d '{{DATFILES}}'
```

This is a parameterised recipe and reusable building block. `PROJFILE`, `OUTFILE`, and `DATFILES` are parameters substituted using the `{{...}}` syntax. By centralising the pydre call here, all targets stay consistent: same flags, same environment, same output format.

> **Note:** The leading tab before `uv run pydre` is required by `just`. Use a real tab character, not spaces.

---

## Extending the Justfile

To add a new analysis, add a new target and wire it into the dependency chain. For example, to add a per-scenario breakdown:

```just
scenarioMetrics: (pydre-run "pydre-projects/scenarios.toml" "out/Metrics_Scenarios.csv" allDatFiles)

outfiles: overallMetrics scenarioMetrics
```

Now `uv run just` will run both `overallMetrics` and `scenarioMetrics` in sequence. No changes to raw data, pydre itself, or the `.env` file are needed.

| To change... | Edit this... |
|--------------|--------------|
| Which data files are processed | `.env` — update `rawdatadir` |
| Which metrics are computed | The relevant `.toml` file in `pydre-projects/` |
| Which analyses run by default | The `outfiles` target in `justfile` |
| Where output files are written | The `OUTFILE` argument in each target |

---

## Troubleshooting

- **`rawdatadir` not found** — Ensure `.env` exists in the project root and `set dotenv-load` is present in the justfile.
- **No `.dat` files matched** — Check the path in `.env` and verify the pattern matches your actual filenames.
- **`just: command not found`** — Install `just` and ensure it is on your `PATH`. See [just.systems](https://just.systems) for platform-specific instructions.
- **Indentation error in justfile** — Recipe bodies must be indented with a real tab character, not spaces.
