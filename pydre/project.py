# -*- coding: utf-8 -*-

import json
import pandas
import re

import pydre.core
import pydre.rois
import pydre.metrics

import logging
logger = logging.getLogger('PydreLogger')


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
		d = pandas.read_csv(filename, sep='\s+', na_values='.')
		datafile_re = re.compile("([^_]+)_Sub_(\d+)_Drive_(\d+)(?:.*).dat")
		match = datafile_re.search(filename)
		experiment_name, subject_id, drive_id = match.groups()
		return pydre.core.DriveData(SubjectID=int(subject_id), DriveID=int(drive_id),
									roi=None, data=d, sourcefilename=filename)

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
		if roi_type == "time":
			logger.info("Processing ROI file " + roi['filename'])
			roi_obj = pydre.rois.TimeROI(roi['filename'])
			return roi_obj.split(dataset)
		elif roi_type == "rect":
			logger.info("Processing ROI file " + roi['filename'])
			roi_obj = pydre.rois.SpaceROI(roi['filename'])
			return roi_obj.split(dataset)
		elif roi_type == "column":
			logger.info("Processing ROI column " + roi['columnname'])
			roi_obj = pydre.rois.ColumnROI(roi['columnname'])
			return roi_obj.split(dataset)
		else:
			return []

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
			logger.warning("Malformed metrics defninition: missing " + str(e))
			return []
		return [report_name, [metric_func(d, **metric) for d in dataset]]

	def loadFileList(self, datafiles):
		"""
		Args:
			datafiles: a list of filename strings (SimObserver .dat files)

		Loads all datafiles into the project raw data list.
		Before loading, the internal list is cleared.
		"""
		self.raw_data = []
		for datafile in datafiles:
			logger.info("Loading file #{}: {}".format(len(self.raw_data), datafile))
			self.raw_data.append(self.__loadSingleFile(datafile))

	def run(self, datafiles):
		"""
		Args:
			datafiles: a list of filename strings (SimObserver .dat files)

		Load all files in datafiles, then process the rois and metrics
		"""
		self.loadFileList(datafiles)
		data_set = []
		if 'rois' in self.definition:
			for roi in self.definition['rois']:
				data_set.extend(self.processROI(roi, self.raw_data))
		else:
			# no ROIs to process, but that's OK
			logger.warning("No ROIs, processing raw data.")
			data_set = self.raw_data

		logger.info("number of datafiles: {}, number of rois: {}".format(len(datafiles), len(data_set)))

		result_data = pandas.DataFrame()
		result_data['Subject'] = pandas.Series([d.SubjectID for d in data_set])
		result_data['DriveID'] = pandas.Series([d.DriveID for d in data_set])
		result_data['ROI'] = pandas.Series([d.roi for d in data_set])
		for metric in self.definition['metrics']:
			metric_title, metric_values = self.processMetric(metric, data_set)
			
			if (metric_title in result_data):
				logger.error("The metric title [" + metric_title + "] occrus multiple times in the project file. Only the last metric named [" + metric_title + "] will be kept in the data.")
				#Should we quit() here??
				
			result_data[metric_title] = pandas.Series(metric_values)
		self.results = result_data	

	def save(self, outfilename="out.csv"):
		"""
		Args:
			outfilename: filename to output csv data to.

		The filename specified will be overwritten automatically.
		"""
		
		try:
			self.results.to_csv(outfilename, index=False)
		except AttributeError:
			logger.error("Results not computed yet")
