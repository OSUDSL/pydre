# -*- coding: utf-8 -*-

import json
import pandas
import re

import pydre.core
import pydre.rois
import pydre.metrics


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
		return pydre.core.DriveData(SubjectID=subject_id, DriveID=drive_id, roi = None, data=d, sourcefilename=filename)

	def processROI(self, roi, dataset):
		"""
		Handles running region of interest definitions for a dataset

		Args:
			roi: A dict containing the type of a roi and the filename of the data used to process it
			dataset: a list of pandas dataframes containing the source data to partition

		Returns:
			A list of pandas DataFrames containing the data for each region of interest
		"""
		roi_type = roi['type']
		filename = roi['filename']
		if roi_type == "time":
			roi_obj = pydre.rois.TimeROI(filename)
			return roi_obj.split(dataset)
			
	def processMetric(self, metric, dataset):
		"""
		Handles running any metric defninition

		Args:
			metric: A dict containing the type of a metric and the parameters to process it

		Returns:
			A list of values with the results
		"""

		try:
			metric_func = pydre.metrics.metricsList[metric.pop('function')]
			report_name = metric.pop('name')
		except KeyError as e:
			pydre.core.logger.warning("Malformed metrics defninition: missing " + str(e))
			return []
		return [metric_func(d, **metric) for d in dataset]

	def loadFileList(self, datafiles):
		raw_data = []
		for datafile in datafiles:
			print(len(raw_data))
			raw_data.append(self.__loadSingleFile(datafile))
		return raw_data
		
	def run(self, datafiles):
		"""Load all files in datafiles, then process the rois and metrics"""
	
		data_set = self.loadFileList(datafiles)
		
		try:
			for roi in self.definition['rois']:
				data_set = self.processROI(roi, data_set)
		except AttributeError as e:
			pydre.core.logger.warning("AttributeError:" + e)
			# no ROIs to process, but that's OK
			data_set = [[x, ] for x in data_set]

		results = []
		
	
		results.append([d.SubjectID for d in data_set])
		
		for metric in self.definition['metrics']:
			results.append(self.processMetric(metric, data_set))
		return results

	def save(self, outfilename):
		try:
			self.results.to_csv(outfilename)
		except AttributeError:
			pydre.logging("Results not computed yet")
