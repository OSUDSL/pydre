---
title: "Installation Guide"
---


Pydre is a Python package, which means it can be installed using a Python package manager. If you are familiar with *pip*, you can use it to install Pydre as well. However, we recommend using *rye* for a more robust and isolated environment.

# Set up a new Pydre project directory with *rye*

# 1. Install Rye

Follow the instructions at [rye's official website](https://rye-up.com/) to install it on your system. You will probably need to restart your terminal after installation.

## 2. Set up your project directory

Create a new project directory and navigate to it:

```
mkdir my_pydre_project
cd my_pydre_project
```

Initialize a Rye project:

```
rye init
```

Add Pydre as a dependency:

```
rye add pydre
```

## 3. Install Dependencies

Rye will install pydre and all dependencies in a virtual environment specific to your project. To sync the dependencies, run:

```
rye sync
``` 

## 4. Verify Installation

Check that Pydre was installed correctly:

```
python -m pydre.run --help
```

The first run of python after installing and syncing may take several seconds while the python system prepares the dependencies. You should see the command-line help output showing available options. 

## 6. Start Using Pydre

Now you can run Pydre with your project files:

```
python -m pydre.run -p your_project_file.toml -o results.csv
```

## Troubleshooting

If you encounter any issues:

1. Check any error messages in the terminal.
2. Verify that your [project file](../explanation/project_files.md) is properly formatted.

# Setting up a development environment

If you want to contribute to Pydre or modify its source code, you can set up a development environment. You will need to clone the Pydre repository but then you can run `rye sync` in the to install all the dependencies and continue from there. If you are more comfortable with *uv*, you can use that instead of *rye*.

