import shutil
import os
import sys

sys.path.append(os.getcwd())

import runCheck

#the filled filed is normally created by hand by the user from the "empty" file
shutil.copy('./referenceOutputFiles/DetachedHouse_noDimensions-areas-filled.csv','./DetachedHouse_noDimensions-areas-filled.csv')

import runSet

