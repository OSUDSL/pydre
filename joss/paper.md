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

# Architecture 

In using Pydre to perform data reduction, researchers create a TOML project file describing the data filters, regions of interest (ROIs), and metric functions     

# Extensibility

Although there are various real-time interactive driving simulation software systems in use in academic and industry settings, they 

# Acknowledgements

# References