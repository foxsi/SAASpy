__author__ = 'schriste'

"""Functions to deal with a collection of SAAS images"""

from pandas import DataFrame
from saaspy.image import image
import numpy as np

class collection(object):
    def __init__(self, file_list):
        nfiles = len(file_list)
        filenames = []
        times = []
        maxval = []
        minval = []
        maxindex_x = []
        maxindex_y = []

        for i, f in enumerate(file_list):
            s = image(f)
            filenames.append(f)
            times.append(s.date)
            maxval.append(s.max)
            minval.append(s.min)
            maxindex_x.append(s.max_index[0])
            maxindex_y.append(s.max_index[1])

        data = {'max': maxval, 'min': minval, 'mindex_x': maxindex_x, 'mindex_y': maxindex_y}
        self.data = DataFrame(data, index=times)


