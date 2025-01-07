---
title: 'Pydre: A Python package for driving simulation data reduction'
tags:
  - Python
  - driving simulation
authors:
  - name: Thomas Kerwin
    orcid: 0000-0000-0000-0000
    affiliation: 1
affiliations:
 - name: The Ohio State University, United States
   index: 1
   ror: 00rs6vg23

bibliography: paper.bib
---

# Summary

The Python package *Pydre* (pronounced pie-dray), provides a cohesive framework for data reduction in the context of driving simulation. 

# Statement of need

Driving simulators are complex pieces of equipment that are extremely valuable in experimental studies on driving behavior. Simulation technology in general is very useful when doing things in real life is too dangerous or too expensive. The types of experimental conditions desired by scientists investigating driving behavior are often both of these things.

The driving simulators commonly used for the investigation of driving behavior generate a moderate amount of time series data (recorded at 30Hz or more) for each scenario run on the sim. Investigators often want to convert that time series data to discrete metrics that describe a specific aspect of how the driver interacted with the vehicle during the drive. These metrics need to be calculated for all participants in a study, and often for multiple scenarios per participant. 

This is a necessary component of the most common type of driving-data based analysis of participant simulator performance. This work could be accompblished by bespoke processing scripts for a particular project. However, these one-off scripts are often not taken seriously as reusable code and can lead to fragile software projects that can not be easily shared between researchers, even at the same lab. In addition, many approaches using multi-stage processing with multiple programs can lead to intermediate data files and data pipelines that can lead to running code on the incorrect "stage" of the data.

*Pydre* attempts to avoid the problems above by offering a unified, modular architecture for reducing data from driving simulators into discrete metrics. It is a single application, designed to be used by all projects and share code among them. The modularity allows different users to add new filters or metric-calculating functions in a separate python file and eventually test and document that code, incorporating it into the general library and allowing easy use for other studies.

# Architecture 

In using Pydre to perform data reduction, researchers write a project file describing the data filters, regions of interest (ROIs), and metric functions that will be applied.  

![Pydre data pipeline](pydre data pipeline.png)


## Data filters

## Regions of interest

## Metric functions

# Extensibility

Although there are various real-time interactive driving simulation software systems in use in academic and industry settings, they use very similar tabular, CSV-like, time-series data formats

# Acknowledgements

The authors would like to thank the many undergraduate researchers who have used and provided feedback on previous versions of the software.

# References