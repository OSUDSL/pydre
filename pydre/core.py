# -*- coding: utf-8 -*-

import collections
import logging
logger = logging.getLogger(__name__)


def namedtuple_with_defaults(typename, field_names, default_values=()):
    T = collections.namedtuple(typename, field_names)
    T.__new__.__defaults__ = (None,) * len(T._fields)
    if isinstance(default_values, collections.Mapping):
        prototype = T(**default_values)
    else:
        prototype = T(*default_values)
    T.__new__.__defaults__ = tuple(prototype)
    return T


DriveData = namedtuple_with_defaults('DriveData', ['SubjectID', 'DriveID', 'roi', 'data', 'sourcefilename'], 
	(None, None, None, None, None))