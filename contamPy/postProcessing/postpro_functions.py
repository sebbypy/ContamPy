import sys
sys.path.append('/home/spec/Documents/Projects/RESEARCH/COMISVENT/2.Work/Python')
sys.path.append('/home/spec/Documents/Softs/PyGUI/WorkingCopy/trunk/guicore_files')
sys.path.append('/home/spec/Documents/Softs/PyGUI/WorkingCopy/trunk/readers_files')

import contam_functions
import pandas as pd
import json

import matplotlib.pyplot as plt
import numpy as np

from CONTAMReader import *
from dfIO import dropperiod


pd.set_option('mode.chained_assignment', None)

def exposure(df,threshold,etype='mean'):

    #assuming 1 columns per occupant
    #etype = 'mean' or 'max' or 'cumulated'

    freq=df.index[1]-df.index[0]


    df=df-threshold


    exp=df[df>0].sum()* (freq/datetime.timedelta(hours=1))

    
    if (exp.describe()['count']==0):
        return 0


    if (etype=='mean'):
    
        return exp.mean()

    elif(etype=='max'):
        return exp.max()
        
    elif(etype=='cumulated'):
        return exp.sum()
    

def flowexposure(df,Qmin,percentile):

    #Qmin = min flow per person #typically 15 to 20 m3/h

    odf=df.filter(regex='^O_',axis=1) # ^ means "starting with"

    rooms=[ x.split('_')[1] for x in odf.columns ]

    for room in rooms:

        if ('Slaapkamer' in room):
            shortroom=room.replace('kamer','')
        else:
            shortroom=room

        #total supply in space
        odf['QS_'+room]=df.filter(regex='^Q_[M-N]S_'+shortroom,axis=1).sum(axis=1)

        #total exract in space
        odf['QE_'+room]=df.filter(regex='^Q_[M-N]E_'+shortroom,axis=1).sum(axis=1)
           
        #Maximum of extract of supply in the room --> suppose that it's ok if extracted air instead of supply
        odf['QM_'+room]=odf[['QE_'+room,'QS_'+room]].max(axis=1)
        
        
        #computing flow deficit PER CAPITA
        odf['E_'+room]=(odf['QM_'+room]/odf['O_'+room]-Qmin)  # *odf['O_'+room] --> per capita : no need to sum
        odf['E_'+room].replace([np.inf, -np.inf], np.nan,inplace=True)   
        ##!!! Warning: there can be deficit in one room, and excess in other --> could compensate if simple sum
        ## to avoid this compensation effect, one should sum separately negative values

    #odf['TotalFlowExposureDeficit']=odf.filter(regex='^E_').sum(axis=1)
    #odf['TotalOccupants']=odf.filter(regex='^O_',axis=1).sum(axis=1)
    #odf['SpecificFlowExposureDeficit']=odf['TotalFlowExposureDeficit']/odf['TotalOccupants']
    #print(odf[['TotalFlowExposureDeficit','TotalOccupants','SpecificFlowExposureDeficit']])
    #odf['SpecificFlowExposureDeficit'].hist(bins=100,histtype='step',density='True',figsize=(10,6),cumulative=True) 

    #odf.filter(regex='^E_').hist(bins=100,histtype='step',density=True,figsize=(10,6))
    #odf.filter(regex='^QM_').hist(bins=100,histtype='step',density=True,figsize=(10,6))
    #plt.show(block=False)
    #input('...')

    #current choice: take the wost deficit at each time step --> not necessarly always the same occupant, but difficult to distinguish them
    odf['WorstFlowDeficit']=odf.filter(regex='^E_').min(axis=1)

    #print(odf['WorstFlowDeficit'].describe())
    #print(odf['WorstFlowDeficit'].isna().sum())
    
    
    fractionoftime= len(odf[odf['WorstFlowDeficit']<0])/len(odf['WorstFlowDeficit'].dropna())

    pflow=odf['WorstFlowDeficit'].quantile(percentile/100).min()+Qmin  #+ Qmin car le deficit est le débit < Qmin --> on revient à des valeurs absolures
    
   
    """print("Fraction of time with too low flow rate ",fractionoftime)
    print("P5 flow",p5flow)
   
    odf['WorstFlowDeficit'].hist(bins=100,histtype='step',density='True',figsize=(10,6),cumulative=True) 
    plt.xlabel('Flow rate exposure above threshold (0 = threshold)')
    #odf['WorstFlowDeficit'].hist(bins=100,histtype='step',density='True',figsize=(10,6),cumulative=False) 
    
    
    plt.show(block=False)
    input('...')
    """
    
    return fractionoftime,pflow


parameters={
    'Year to assign':2020,
    'Filters':'^Q_*;^CO2_*;^H2O_*;^VOC_*;^O_*',
    'Load ach file?':False,
}

contamlog=sys.argv[1]


print("contamlog",contamlog)

df=loadCONTAMlog().execute(contamlog,parameters)

dropperiod(df,datetime.datetime(2020,4,1),datetime.datetime(2020,9,30),inplace=True)



if (os.path.exists('Allres.csv')):
    rdf=pd.read_csv('AllRes.csv',index_col=0)
else:
    rdf=pd.DataFrame()

# 1. Exposure above a certain threshold or percentiles
######################################################

expodf=df.filter(regex='CO2_O[0-9]', axis=1)

#expodf.hist(bins=100,cumulative=True,histtype='step',density=True)
#plt.show(block=False)
#input('...')

#print("Mean exposure above 1000: ",exposure(expodf,1000), 'ppm.h')
#print("Max exposure above 1000: ",exposure(expodf,1000,'max'), 'ppm.h')
#print("Max p95 :",expodf.quantile(.95).max(),'ppm.h')

rdf.loc[contamlog,'e1000-mean [ppm.h]']=exposure(expodf,1000)
rdf.loc[contamlog,'e1000-max [ppm.h]']=exposure(expodf,1000,'max')
rdf.loc[contamlog,'p95-max [ppm]']=expodf.quantile(.95).max()



# 1.1 VOC (= polluant fictif)
vocdf=df.filter(regex='VOC_O[0-9]', axis=1)

#(vocdf*1000).plot()
#plt.show(block=False)
#input('...')
#exit()

rdf.loc[contamlog,'VOC-15-max [g/kg.h]']=exposure(vocdf*1e3,15,'max')



print(exposure(vocdf*1e3,15,'max'))



# 2. Exposure to flow rate
##########################

#ftime=flowexposure(df,15)
qmin=15
percentile=10
f,p=flowexposure(df,qmin,percentile)

rdf.loc[contamlog,'Time fratction Qocc<'+str(qmin)+' m3/h [-]']=f
rdf.loc[contamlog,'p'+str(percentile)+' of flow rate exposure [m3/h]']=p


#3. H2O criteria
#################

maxhours=0

freq=df.index[1]-df.index[0]
oneh=datetime.timedelta(hours=1)


for c in df.filter(regex="H2O_",axis=1).columns:
    
    habove70 = int(df[c][df[c]>0.7].count()*(freq/oneh))

    maxhours=max(maxhours,habove70)
    
    print(c,habove70)

rdf.loc[contamlog,'Hours above 70pc RH - max']=maxhours


rdf.to_csv('Allres.csv')



