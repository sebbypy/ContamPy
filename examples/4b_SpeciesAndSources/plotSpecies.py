# Plot mechanical flow rates
import sys
import os

currentPath = os.getcwd()
srcPath = os.path.join(currentPath,'..','..','src')

sys.path.append(os.path.join(srcPath,'postProcessing'))

from postpro_functions import readContamLog
import pandas as pd
import matplotlib.pyplot as plt


def filterNullColumns(df):

    stats = df.describe()
    columnsToDrop = []

    for c in list(df.columns):
        if abs(stats.loc['mean',c]) < 0.001 and stats.loc['std',c]< 0.001:
            columnsToDrop.append(c)
            
    return df.drop(columns=columnsToDrop)
    


df = readContamLog('MHRV-RIJ2-BALANCED.log')


for specie in ['HCHO','FIC','PM2.5','CO2']:

    occupantExposure = df.filter(regex=specie+'_O')
    occupantExposure.plot(figsize=(10,6),grid=True,title='Occupant exposure to '+specie)

    plt.ylabel(specie+' concentration seen by occupants')
    plt.savefig(specie+".pdf")



plt.close('all')