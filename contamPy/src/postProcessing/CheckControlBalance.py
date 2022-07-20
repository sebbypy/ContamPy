import sys

sys.path.append('/home/spec/Documents/Softs/PyGUI/WorkingCopy/trunk/guicore_files')
sys.path.append('/home/spec/Documents/Softs/PyGUI/WorkingCopy/trunk/readers_files')

import matplotlib.pyplot as plt
import numpy as np

from CONTAMReader import *

parameters={
    'Year to assign':2020,
    'Filters':'Q_*;CO2_*;H2O_*',
    'Load ach file?':False,
}

contamlog=sys.argv[1]

df=loadCONTAMlog().execute(contamlog,parameters)

suptot=df.filter(regex='Q_MS', axis=1).sum(axis=1)
exttot=df.filter(regex='Q_ME', axis=1).sum(axis=1)

dftot=pd.DataFrame()
dftot['Q_MS_tot']=suptot
dftot['Q_ME_tot']=exttot
dftot['balance']=dftot['Q_MS_tot']-dftot['Q_ME_tot']

print(dftot.describe())


