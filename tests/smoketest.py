#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(os.getcwd())

import pydre.project
import pydre.core
import os.path
import glob
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

p = pydre.project.Project("docs/test_pf.json")

# put some data files in tests/testdata/ to test it out
filelist = glob.glob(os.path.join(os.path.dirname(__file__), 'testdata/*.dat'))

r = p.run(filelist, "CWS_Output.csv")
print(r)
