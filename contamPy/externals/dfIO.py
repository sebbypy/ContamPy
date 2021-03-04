# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 12:29:08 2019

@author: spec
"""

#import matplotlib.pyplot as plt

import pandas as pd
import numpy as np
import datetime


def basicinfo(df,title):
    
    nrows,ncols=df.shape
    
    text=''
    text+='Dataframe : '+str(title)+'\n'
    text+='\n'
    text+='Start time : '+str(df.index[0])+'\n'
    text+='End time  : '+str(df.index[-1])+'\n'
    text+='\n'
    text+='Number of rows : '+str(nrows)+'\n'
     
    text+='\n'
    text+='Number of columns : '+str(ncols)+'\n'
    text+='  Names: \n'
    for c in df.columns:
        nbnan=0
        nbnan=df[c].isnull().sum()
        text+='      '+c
        
        if (nbnan>0):
            text+=' ( '+str(nbnan)+' nan values)'

        text+='\n'


    return text

    

def print_full(x):
    """pd.set_option('display.max_rows', len(x))
    pd.set_option('display.max_columns', len(x.columns))
    
    pd.set_option('display.max_columns', len(x.columns))
    z=pd.get_option('display.max_colwidth')
    pd.set_option('display.max_colwidth',150)
    print(z)
    y=str(x)
    print(x)
    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')
    pd.reset_option('display.max_colwidth')
    """
    
    
    return(x.to_string(line_width=150))

        



def dfappend(dflist):
    
    newdf=pd.DataFrame()
    
    for df in dflist:
        newdf=newdf.append(df)
        
    newdf=newdf.sort_index()
        
    return newdf

#def get_duplicate_cols(df: pd.DataFrame) -> pd.Series:
#    return pd.Series(df.columns).value_counts()[lambda x: x>1]
    
    
def fillField(df,tofill,filler):
    
    df[tofill][np.isnan(df[tofill])]=df[filler][np.isnan(df[tofill])]
    
    
    
    
        
def replaceValues(df,tofill,symbol,initval,newval):
    
    fnewval=float(newval)
    finitval=float(initval)
    
    if (symbol == '=') :
    
        df[tofill][df[tofill]==finitval] = fnewval
        
    elif symbol=='<' :
        df[tofill][df[tofill]<finitval] = fnewval
        
    else : #symbol=='>'
        df[tofill][df[tofill]>finitval] = fnewval
        
    

def evaluate_expression(df,expression,newname):
    
    operators=['+','*','/','-','(',')','**']

    fields=expression

    for o in operators:
        fields=fields.replace(o,';')   
    
    fields=fields.split(';')
    
    fields = [ x.strip() for x in fields]

    #print("Fields",fields)

    ok=True

    equationtoevaluate=expression
    for field in fields:
    
        if ( not isfloat(field) and (field not in df.keys())):
            message='Field "'+field+'" does not exist in the loaded dataframe. Check your equation is correct'
            #print("message",message)
            ok=False
    
        if (not isfloat(field)):
    
            equationtoevaluate=equationtoevaluate.replace(field,'df["'+field+'"]')
 
    
    

    if (ok):
        z=eval(equationtoevaluate)
        message='Ok added field!'
        
        df[newname]=z
        
    return ok,message
    



def addprefixandsuffix(df,prefix,suffix):

    matchdict={}    
    
    #for col in GUI.panesLayouts[datatype].Lists['loaded'+datatype].DFS[dfname]:
    for col in df.columns:
        matchdict[col]=prefix+col+suffix
        
    df.rename(columns=matchdict,inplace=True)



def dropperiod(df,fromdate,todate,inplace=False):
 
    #print(fromdate)
    #print(todate)

    todate=todate+datetime.timedelta(days=1)
    
    
    index_to_drop = df.index[(df.index >= pd.to_datetime(fromdate)) & (df.index <= pd.to_datetime(todate) )]


        
    if (inplace==True):
        df.drop(index_to_drop,inplace=True)
        
    else:
        
        return df.drop(index_to_drop)
   



def RenameDuplicated(df):
    
    
    while df.columns.has_duplicates:
        
        #print("in loop")

        for i,duplicated in zip( range(len(df.columns)) , df.columns.duplicated() ):
            #print("i",i)
            #print("df.columns",df.columns)
            #print("dupli",duplicated)
            if (duplicated==True):
                newnames=list(df.columns)
                newnames[i]+='-d'
                df.columns=newnames

    return 


def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False




def dfmerge(dflist,reindex=False,refindex=0,suffixes=None,tolerance='30min'):
    
    # merge = columns side by side
    
    # dflist = list of df to merge ()
    # reindex = reindex all tables with the same index
    # refindex = df whose index will be taken (first one by defulat)
    # suffixes = suffixes to add to each original column name in cas of duplicates
    # tolerance = maximum time shift for which data are filled
    
    if (suffixes==None):
        suffixeslist=[ '' for df in dflist]
    else:
        suffixeslist=suffixes
    
    if (reindex):
        newindex=dflist[refindex].index
    
        print(newindex)
    
    newdf=pd.DataFrame()

    
    for df,suffix in zip(dflist,suffixeslist):

        #print(df.index)
        #print("Suffix",suffix)
        
        if (suffix != ''):
            newcolnames={ c:c+suffix for c in df.columns}
            tmpdf= df.rename(columns=newcolnames)
        else:
            tmpdf=df
     
        if (reindex):
            reindexeddf=tmpdf.reindex(newindex,method='nearest',tolerance=pd.to_timedelta(tolerance))
            tmpdf=reindexeddf
        
        
        newdf= pd.concat([newdf, tmpdf], axis=1, sort=False)
        #newdf=pd.append()


    #remove possible remaining duplicates if suffixes have not been defined
    if (newdf.columns.has_duplicates):
        newcols=[]
        #print("inducplicats")    
        for i in range(len(newdf.columns)):
            if newdf.columns.duplicated()[i]==True:
                newcols.append(newdf.columns[i]+'_1')
            else:
                newcols.append(newdf.columns[i])
        newdf.columns=newcols
        
          
        #msgBox = QMessageBox()
        #msgBox.setWindowTitle("Warning !")
        #msgBox.setText('Some duplicates columns were found, which is not expected when merging files.\n They were renamed with a suffix _1. Please check the output before using them')
        #msgBox.setStandardButtons(QMessageBox.Ok)
        #msgBox.buttonClicked.connect(msgButtonClick)

        #returnValue = msgBox.exec()
        #if returnValue == QMessageBox.Ok:
        #    print('OK clicked')
    
    return newdf






