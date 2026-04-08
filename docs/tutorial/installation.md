---
title: "Installation Guide"
---

Pydre is a Python package that can be installed using a Python package manager. While pip works, we recommend using *uv* for a more robust and isolated environment.

# Set up a new Pydre project directory with *uv*

## 1. Install UV

Follow the instructions at [uv's official website](https://docs.astral.sh/uv/) to install it on your system. You will likely need to restart your terminal after installation.

## 2. Set up your project directory

Create a new project directory and navigate to it:

```
mkdir my_pydre_project
cd my_pydre_project
```

Initialize a uv project:

```
uv init
```

Add Pydre as a dependency:

```
uv add pydre
```

## 3. Install Dependencies

uv will install pydre and all dependencies in a virtual environment specific to your project. To sync the dependencies, run:

```
uv sync
``` 

## 4. Verify Installation

Check that Pydre was installed correctly:

```
uv run pydre --help
```

The first run of python after installing and syncing may take several seconds while the python system prepares the dependencies. You should see the help output showing available command line options. 

## 5. Start Using Pydre

Now you can run Pydre with your [project files](../explanation/project_files.md) :

```
uv run pydre -p your_project_file.toml -o results.csv
```

To run a specific analysis target using just:
```
uv run just overallMetrics
```

If you want to try an example project file, follow along with the [Basic Analysis tutorial](basic_analysis.md).


## Troubleshooting

If you encounter any issues:

1. Check any error messages in the terminal.
2. Verify that your [project file](../explanation/project_files.md) is properly formatted.
3. If you are still having problems, please [open an issue on GitHub](https://github.com/OSUDSL/pydre/issues).


# Setting up pydre with *pip*

## 1. Install Python

Ensure you have Python installed on your system. You can download it from [python.org](https://www.python.org/).

## 2. Set up your project directory

Create a new project directory and navigate to it:

```bash
mkdir my_pydre_project
cd my_pydre_project
```

## 3. Create a virtual environment

Set up a virtual environment to isolate your project dependencies:

```bash
python -m venv venv
```

Activate the virtual environment:

- On Windows:
  ```bash
  venv/Scripts/activate
  ```
- On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

## 4. Install Pydre

Use pip to install Pydre:

```bash
pip install pydre
```

### 5. Verify Installation

Check that Pydre was installed correctly:

```bash
pydre --help
```

You should see the help output showing available command line options.

---
**Next Step:** [Basic Analysis Guide](basic_analysis.md)
---

# Setting up a development environment

If you want to contribute to Pydre or modify its source code, you can set up a development environment. You will need to clone the Pydre repository:

```bash
git clone https://github.com/OSUDSL/pydre.git
cd pydre
uv sync
uv run pytest
```

If you are more comfortable with *rye*, you can use that instead of *uv*.



