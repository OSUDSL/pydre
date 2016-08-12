import os
from setuptools import setup
import setuptools




setup(
	name = "pydre",
	version = '0.2',
	description = "The script is used to package the modules in pydre into a wheel file ",
	packages = ["pydre"],
	py_modules = ["pydre_run", "pydre_merge", "smoketest"],
	install_requires=['pandas'],
)