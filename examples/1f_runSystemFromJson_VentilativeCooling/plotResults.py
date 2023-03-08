# Plot mechanical flow rates
import sys
import os

currentPath = os.getcwd()
srcPath = os.path.join(currentPath,'..','..','src')

sys.path.append(os.path.join(srcPath,'postProcessing'))

from postpro_functions import readContamLog
import pandas as pd
import matplotlib.pyplot as plt


logFileWithPath = 'MHRV-And-VentilativeCooling.log'

contamLogDF = readContamLog(logFileWithPath).filter(regex='C_NS|C_VC|T_')

controls = contamLogDF.filter(regex='C_NS|C_VC')

others = contamLogDF.filter(regex='T_')

print(controls.describe().to_string())

print(others.describe().to_string())

