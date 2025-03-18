# Contributing

Thank you for contributing to `pydre`! 

If you have suggestions, bug reports, or code contributions, please open an issue or a pull request.

The [GitHub "Issues" tab](https://github.com/OSUDSL/pydre/issues) can be used to track bugs and feature requests. 

## Bug reports
Bug reports from users are important for identifying unintentional behavior. If you find a bug, please open a new issue with the following:

1. An explanation of the problem with enough details for others to reproduce the problem. Some  common information needed is:
    * Operating system
    * Python version
    * Any commands executed (perhaps a python snippet)
    * An error message from the terminal
2. An explanation of the expected behavior. For example:
    * I ran `numpy.add(1,2)` which gave me an output of `-999`, but I expected `3`. 


## Development Environment
In order to add new features to `pydre` you need to set up a working development environment.
First, you must create a [fork](https://github.com/OSUDSL/pydre/fork). Then use the following 
commands. "your-fork" is a placeholder for the location of your fork of `pydre`.

```bash
# 1. Download source code
git clone git@github.com:your-fork/pydre.git  # requires ssh-keys
# or 
git clone https://github.com/your-fork/pydre.git
# 2. Open the pydre directory
cd osier
# 3. Add a remote to the official repository
git remote add OSUDSL https://github.com/OSUDSL/pydre.git  # the official repository
# 4. Update osier
git pull OSUDSL main  # pull down the up-to-date version of osier
```


## Making a pull request
A good pull request requires the following, along with a new feature (where applicable)
1. All functions should have docstrings using the [Google style](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).
2. All new functions should have corresponding unit tests (and should be small enough that unit-testing makes sense).
3. All tests must pass on your machine by running `pytest` in the top level directory.
4. All new features must be appropriately documented.
5. Code should follow [PEP8 style](http://www.python.org/dev/peps/pep-0008/). [`autopep8`](https://pypi.org/project/autopep8/) is a helpful tool for ensuring consistent style.