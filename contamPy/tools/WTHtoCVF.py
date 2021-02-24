

import sys
sys.path.append('/home/spec/Documents/Projects/RESEARCH/COMISVENT/2.Work/Python')
sys.path.append('/home/spec/Documents/Softs/PyGUI/WorkingCopy/trunk/guicore_files')
sys.path.append('/home/spec/Documents/Softs/PyGUI/WorkingCopy/trunk/readers_files')

import contam_functions
from CONTAMReader import *


weather=sys.argv[1]
cvf=sys.argv[2]

wdf=loadCONTAMWeather().execute(weather,{'Year to assign':2021})
writeCVF().execute(wdf['Ws [m/s]'],'./test.cvf',{})

