# Plot mechanical flow rates
import sys
import os

currentPath = os.getcwd()
srcPath = os.path.join(currentPath,'..','..','src')

sys.path.append(os.path.join(srcPath,'postProcessing'))

from postpro_functions import readContamLog
import pandas as pd
import matplotlib.pyplot as plt


logFileWithPath = 'VentilativeCooling.log'

contamLogDF = readContamLog(logFileWithPath).filter(regex='Q_VC|C_VC|T_')

controls = contamLogDF.filter(regex='C_VC')

flows = contamLogDF.filter(regex='Q_VC')

temperatures = contamLogDF.filter(regex='^T_')-273.15

print(controls.columns)
print(flows.columns)
print(temperatures.columns)


fig, axs = plt.subplots(3)
fig.suptitle('Ventilative cooling case')

temperatures.plot(ax=axs[0])
controls.plot(ax=axs[1])

flows.plot(ax=axs[2])

plt.show()
#☺axs[0].plot(x, y)
#axs[1].plot(x, -y)