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
    


df = readContamLog('MHRV-RIJ2-DCV-BALANCED.log')

df = filterNullColumns(df)


supplyFlows = df.filter(regex='Q_MS')
extractFlows = df.filter(regex='Q_ME')

supplyFlows.plot(figsize=(10,6),grid=True,title='Supply flow rates')
plt.ylabel('Flow rate [m³/h]')
plt.savefig("supplyFlows.pdf")

extractFlows.plot(figsize=(10,6),grid=True,title='Extract flow rates')
plt.ylabel('Flow rate [m³/h]')
plt.savefig("extractFlows.pdf")

totalFlows = pd.DataFrame(index=df.index,columns=['Total MS','Total ME'])
totalFlows['Total MS']=supplyFlows.sum(axis=1)
totalFlows['Total ME']=extractFlows.sum(axis=1)


totalFlows.plot(style=['-','--'],figsize=(10,6),grid=True,title='Balance between total supply and extract flow rates')
plt.ylabel('Flow rate [m³/h]')
plt.savefig("flowBalance.pdf")





