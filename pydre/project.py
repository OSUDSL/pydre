#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import pandas
import re

import pydre.core
import pydre.rois

class Project():
	def __init__(self, projectfilename):
		self.project_filename = projectfilename
		self.definition = None
		with open(self.project_filename) as project_file:
			self.definition = json.load(project_file)

		# TODO: check for correct definition syntax
		self.data = []


	def __loadSingleFile(self, filename):
		"""Load a single .dat file (whitespace delmited csv) into a DriveData object"""
		# Could cache this re, probably affect performance
		d = pandas.read_csv(filename, sep=' ', na_values='.')
		datafile_re = re.compile("([^_]+)_Sub_(\d+)_Drive_(\d+).dat")
		match = datafile_re.match(filename)
		experiment_name, subject_id, drive_id = match.groups()
		return pydre.core.DriveData(SubjectID=subject_id, DriveID=drive_id, data=d, sourcefilename=filename)


	def processROI(roi, dataset):
		"""
		Handles running region of interest definitions for a dataset

		Args:
			roi: A dict containing the type of a roi and the filename of the data used to process it

		Returns:
			A list of pandas DataFrames containing the data for each region of interest
		"""
		try

	def run(self, datafiles):
		"""Load all files in datafiles, then process the rois and metrics"""
		raw_data = []
		for datafile in datafiles:
			raw_data.append(self.__loadSingleFile(datafile))

		data_set = []
		try:
			for roi in self.definition.rois:
				data_set.append(self.processROI(roi))
		except AttributeError:
			# no ROIs to process, but that's OK
			data_set = raw_data
			

		try:
			for metric in self.definition.metrics:
				pass
		except AttributeError:
			print("No metrics to process!")

	def save(self, outfilename):
		try:
			self.results.to_csv(outfilename)
		except AtrributeError:
			pydre.logging("Results not computed yet")
