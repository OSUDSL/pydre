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
logging.basicConfig(level=logging.INFO)

p = pydre.project.Project("docs/test_pf.json")

# put some data files in tests/testdata/ to test it out
filelist = glob.glob(os.path.join(os.path.dirname(__file__), 'testdata/CWS2_Sub_16_*.dat'))
p.run(filelist)
p.save()
