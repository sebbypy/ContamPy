import sys

import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

import os

postproDir = os.path.dirname(os.path.realpath(__file__))
externalsDir = os.path.join(postproDir,'..','externals')
sys.path.append(externalsDir)


from CONTAMReader import loadCONTAMlog


pd.set_option('mode.chained_assignment', None)


