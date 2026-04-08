# Getting Started with Pydre

Pydre is a package for analyzing driving simulator data. It takes raw data files from a simulation run, applies a set of metrics you define, and produces an aggregated CSV output you can use for further analysis.

This tutorial walks you through everything you need to go from installation to a fully automated analysis. Here's an overview of what each step covers:

## 1. Installation
Before you can use Pydre, you need to install it and set up a project directory. We recommend using uv, a modern Python package manager that handles dependencies in an isolated environment automatically. If you prefer, Pydre can also be installed with standard pip.

By the end of this step you'll have Pydre installed and be able to run `pydre --help` to confirm everything is working.

## 2. Basic Analysis
With Pydre installed, the next step is learning how to run it. Pydre is driven by a project file, a TOML file where you define which metrics to compute and which regions of your data to focus on. You point Pydre at a project file and a data file, and it produces a CSV of aggregated results.

This step walks through creating your first project file and running it on example data, so you can see exactly what the inputs and outputs look like end-to-end.

## 3. Custom Metrics
Pydre ships with a library of built-in metric functions, but you can also write your own. A custom metric is a Python function that receives a part of the driving data and returns a computed value. Custom metrics live outside the Pydre codebase in your own project directory, and you register them by pointing your project file at the folder containing them.

This step covers how to write, register, and use a custom metric, including best practices for error handling and working with the data structures Pydre provides.

## 4. Setting Up Just
Once your analysis is working, you'll want a repeatable way to run it, especially if you're processing many data files or running multiple analyses. `just` is a command runner that lets you define named targets in a justfile, encoding exactly which project files, data paths, and output locations to use. Combined with a .env file for machine-specific paths, this makes your analysis easy to share with teammates and run consistently across machines.

This step walks through creating a justfile that automates your Pydre runs so that a full analysis pipeline is a single command: `uv run just`

-----
By the end of this tutorial you'll have a working, automated Pydre project that you can adapt to your own simulator data and analysis needs. Start with the [Installation](installation.md) guide to get set up.