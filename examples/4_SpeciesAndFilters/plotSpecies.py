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
    


df = readContamLog('MHRV-RIJ2-BALANCED-FILTERS.log')
df = filterNullColumns(df)


PM25Concentrations = df.filter(regex='PM2.5_')
PM10Concentrations = df.filter(regex='PM10_')


PM25Concentrations.plot(figsize=(10,6),grid=True,title='PM2.5 concentration in the different spaces')
plt.ylabel('PM2.5 Concentration')
plt.savefig("concentrationsPM25.pdf")

PM10Concentrations.plot(figsize=(10,6),grid=True,title='PM10 concentration in the different spaces')
plt.ylabel('PM10 Concentration')
plt.savefig("concentrationsPM10.pdf")


