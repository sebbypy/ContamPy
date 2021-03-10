import sys
import os

postproDir = os.path.dirname(os.path.realpath(__file__))
externalsDir = os.path.join(postproDir,'..','externals')

sys.path.append(externalsDir)

import pandas as pd

from CONTAMReader import loadCONTAMlog
from dfIO import dropperiod
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import numpy as np
import datetime

pd.set_option('mode.chained_assignment', None)


def exposure(df,threshold,etype='max',debug=False):

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
    
def maxHoursAboveThreshold(df,threshold,debug=False):

    maxHours=0

    freq=df.index[1]-df.index[0]
    oneh=datetime.timedelta(hours=1)

    for c in df.columns:
    
        hoursAboveThreshold = int(df[c][df[c]>threshold].count()*(freq/oneh))

        if (debug):
            print(c,hoursAboveThreshold)

        maxHours=max(maxHours,hoursAboveThreshold)


    return maxHours


def getIaqIndicators(df,debug=False):

    year = df.index[0].year
    
    dropperiod(df,datetime.datetime(year,4,1),datetime.datetime(year,9,30),inplace=True)
    
    occupantsCO2 = df.filter(regex='CO2_O[0-9]', axis=1)
    co2Exposure = exposure(occupantsCO2,1000,'max',debug)

    occupantsVOC = df.filter(regex='VOC_O[0-9]', axis=1)
    vocExposure = exposure(occupantsVOC*1e3,15,'max',debug)

    h2oRooms = df.filter(regex="H2O_",axis=1)
    h2oHours = maxHoursAboveThreshold(h2oRooms,0.7,debug)



    return {'CO2 Exposure':co2Exposure,
            'VOC Exposure':vocExposure,
            'H2O Hours':h2oHours
            }



def renameduplicates(df):
    cols=pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique(): 
        cols[cols[cols == dup].index.values.tolist()] = [dup + '.' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]
    # rename the columns with the cols list.
    df.columns=cols
    return(df)


def readDataBaseFromFile(dataBase):
    
    if os.path.exists(dataBase):
        df = pd.read_csv(dataBase,index_col=0)
        return df
        
    else:
        print("Could not read database")
        return
     

def readContamLog(contamlog):

    parameters={
        'Year to assign':2020,
        'Filters':'Q_*;CO2_*;H2O_*;^O_*;VOC_*',
        'Load ach file?':False,
    }

    df=loadCONTAMlog().execute(contamlog,parameters)
    df=renameduplicates(df)
    
    return df
    

def selectOneDay(df,date):
    
    #date in d/M format
    day,month=date.split('/')
    day=int(day)
    month=int(month)
    
    #retainin gonly the wanted day
    df=df.loc[[ (x.month==month and x.day==day) for x in df.index ],:]

    return df
    
    
def setOneDayPlots(df,caseID,caseParameters):
    
    figures = {}  # dict  { name: figure_object }
    
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
        
        plt.subplots_adjust(left=0.05,right=0.85,bottom=0.05)
        
        fig.suptitle('Characteristic evolution in "'+o+'" spaces',fontsize=16)
    
        #hfmt=mdates.DateFormatter('%H')
    
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
    
    
    
        createParametersLegendBox(caseParameters)
    
        figures[str(caseID)+'-singleDay-'+o]= fig
        
        
    return figures
        

def createParametersLegendBox(parametersDict):

    #original fuction
    #def paramsannotate(simid,paramsdf,parameters_in_legend):


    bbox_props = dict(boxstyle="square", fc="w", ec='black', alpha=1.0)

    if (len(parametersDict)>0):

        annotation_text='Main parameters\n\n'
        
        maxlen=np.max([len(x) for x in parametersDict.keys()])
        #maxlen=np.min([10,maxlen])


        for paramName,paramValue in parametersDict.items():  

            annotation_text+=paramName.ljust(maxlen)+' : '+str(paramValue)+'\n'
          
        
        annotation_text=annotation_text.strip('\n')
        plt.annotate(annotation_text,(.865,.60),xycoords='figure fraction',bbox=bbox_props,fontsize=10,family='monospace',horizontalalignment='left', verticalalignment='top')




def showInteractive():
    
    plt.show(block=False)
    input('...')


def getOneDayFiguresDict(db,logNameWithPath,fullDataFrame,date):

    df = selectOneDay(fullDataFrame,date)

    dirName = os.path.dirname(logNameWithPath)    
    shortLogName = os.path.basename(logNameWithPath)
    caseID = int(shortLogName.split('.')[0])

    caseParameters = db.loc[caseID,:].to_dict()
    
    figures = setOneDayPlots(df,caseID,caseParameters)

    figuresWithFullPath = { os.path.join(dirName,k):v for k,v in figures.items() } # same containter structure, but figure name with full path

    return figuresWithFullPath


def saveFiguresToFiles(figures,fileFormat):
    
    for name,figure in figures.items():
        
        figFileName = name+'.'+fileFormat
                    
        figure.savefig(os.path.join(figFileName))

        plt.close(figure)



def plotAndSaveOneDayFigures(db,logNameWithPath,fullDataFrame,date,fileFormat):
       
    figures=getOneDayFiguresDict(db,logNameWithPath,fullDataFrame,date)
    saveFiguresToFiles(figures,fileFormat)
 


if __name__ == '__main__':
    

    if (len(sys.argv)<2):
        print("Usage ")
        print("")
        print("python postpro_functions.py contamLog")
        exit()

    action = sys.argv[1]  # IAQ or plot1Day
    logNameWithPath = sys.argv[2]

    fullDataFrame = readContamLog(logNameWithPath)

    if (action == 'plot1Day'):
      
        date,fileFormat = sys.argv[3:5]

        db = readDataBaseFromFile('SimulationDataBase.csv')

        figuresDict = getOneDayFiguresDict(db,logNameWithPath,fullDataFrame,date)
    
        if (fileFormat == 'interactive'):
            showInteractive()    
        else:
            saveFiguresToFiles(figuresDict,fileFormat)


    elif (action =='IAQ'):

 
        indicators = getIaqIndicators(fullDataFrame,True)
    
        print("CO2 exposure",indicators['CO2 Exposure'],"ppm.h")
        print("VOC exposure",indicators['VOC Exposure']*1e3,"g/kg . h")
        print("Hours above 70% RH",indicators['H2O Hours'],"hours")
    

    else:
        print("First argument should be 'IAQ' or 'plot1Day'")
        