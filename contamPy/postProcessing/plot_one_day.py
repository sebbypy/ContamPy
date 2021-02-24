import sys
sys.path.append('/home/spec/Documents/Projects/RESEARCH/COMISVENT/2.Work/Python')
sys.path.append('/home/spec/Documents/Softs/PyGUI/WorkingCopy/trunk/guicore_files')
sys.path.append('/home/spec/Documents/Softs/PyGUI/WorkingCopy/trunk/readers_files')

import contam_functions
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

from CONTAMReader import *

import sys

pd.set_option('mode.chained_assignment', None)


def renameduplicates(df):
    cols=pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique(): 
        cols[cols[cols == dup].index.values.tolist()] = [dup + '.' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]
    # rename the columns with the cols list.
    df.columns=cols
    return(df)


if (len(sys.argv)<1):
    print("Usage ")
    print("")
    print("python plot_one_day.py contam.log d/m (optional:'png')")
    


savepng=False



parameters={
    'Year to assign':2020,
    'Filters':'Q_*;CO2_*;H2O_*;^O_*;VOC_*',
    'Load ach file?':False,
}

contamlog=sys.argv[1]
date=sys.argv[2]  # format DD/MM

if (len(sys.argv)>3):
    
    if (sys.argv[3] == 'png'):
        savepng=True


day,month=date.split('/')
day=int(day)
month=int(month)

df=loadCONTAMlog().execute(contamlog,parameters)
df=renameduplicates(df)

#retainin gonly the wanted day
df=df.loc[[ (x.month==month and x.day==day) for x in df.index ],:]


split=contamlog.split('/')[-1].split('-')

building=split[0]+'-'+split[1]+'-'+split[2]
system=split[3]
control=split[4]
occupancy=split[5]

longtitle=building+' '+system+' '+control+' '+occupancy


options=['dry','wet']

for o in options:

    if (o=='dry'):

        dry=df.filter(regex=r'(Woon|Slaap|Bureau|OKeu)')

        rooms=list(set([ x.split('_')[-1] for x in dry.filter(regex='^O_').columns] ))
        rooms.sort()
        
        mainspecie='CO2'
        mainunit='ppm'

    if (o=='wet'):
    
        wet=df.filter(regex=r'(Keu|OKeu|WC|Was|Bad|Slaap)')

        rooms=list(set([ x.split('_')[-1] for x in wet.filter(regex='^O_').columns] ))
        rooms.sort()

        mainspecie='H2O'
        mainunit='-'

    fig, axes = plt.subplots(nrows=4,ncols=len(rooms),sharey='row',figsize=(18,8))
    
    fig.suptitle(longtitle,fontsize=16)

    hfmt=mdates.DateFormatter('%H')

    for i in range(len(rooms)):

        if (len(rooms[i])>10):
            shortroom=rooms[i].replace('kamer','')
        else:
            shortroom=rooms[i]

        axes[0,i].plot(df.index,df['O_'+rooms[i]])
        axes[0,i].set_title(rooms[i])
            
        axes[1,i].plot(df.index,df[mainspecie+'_'+rooms[i]])

        axes[2,i].plot(df.index,df['VOC_'+rooms[i]]*1e3 )
        
        
        flow=df.filter(regex='Q_[M,N][S,E]_'+shortroom,axis=1) #.plot(ax=axes[2,i])


        for col in flow.columns:
            lab=col.split('_')[0]+'_'+col.split('_')[1]

            if(len(col.split('.'))>1):
                lab+=col.split('.')[-1]

            if(df[col].mean() != 0):
                
                axes[3,i].plot(df.index,df[col],label=lab)



    axes[0,0].set_ylabel('Occupancy [-]')
    axes[1,0].set_ylabel(mainspecie+'['+mainunit+']')
    axes[2,0].set_ylabel('VOC')

    axes[3,0].set_ylabel('Flow rate [m3/h]')


    for i in range(4):
        for j in range(len(rooms)):
            
            if (not len(axes[i,j].lines)):
                axes[i,j].plot(df.index,np.zeros(len(df)),ls='')
            
            axes[i,j].grid(True)
            
            myFmt = mdates.DateFormatter('%H')
            axes[i,j].xaxis.set_major_formatter(myFmt)
                    
            if (j>0):
            
                axes[i,j].yaxis.set_tick_params(labelleft=True)
                
            if (i==3):
                axes[i,j].legend()


    if (savepng):
        plt.savefig(contamlog.replace('.log','day-'+o+'.svg'))
    else:
        plt.show(block=False)
        input('...')
