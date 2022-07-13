import sys
import os
#sys.path.append('/home/spec/Documents/Projects/RESEARCH/COMISVENT/2.Work/Python')
dirPath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dirPath,'..','contamFunctions'))



import contam_functions
import numpy as np
import pandas as pd
import itertools


def checkContamPlan(fname):

    root=fname.replace('.prj','')
    
    contam_data=contam_functions.loadcontamfile(fname)
    
    
    levels=contam_data['levels']
    zones=contam_data['zones']
    flowpaths=contam_data['flowpaths']
    rooms=zones.df[zones.df['flags']!=10]
    
    
    
    #--------------------------------------------------------
    # Checking that there is a supply or return in each room
    #--------------------------------------------------------
    
    ahs=contam_data['ahs']
    ahsreturn=ahs.df.loc[1,'zr#']
    ahssupply=ahs.df.loc[1,'zs#']
    
    for roomid in rooms.index:
    
        if (len(flowpaths.df[ (flowpaths.df['pzn']==roomid) & (flowpaths.df['pzm'] == ahsreturn) ]) < 1):
            print("There is no mechanical return device in room ",rooms.loc[roomid,'name'])
            print("Check failed")
            exit()
            
        if (len(flowpaths.df[ (flowpaths.df['pzn']==ahssupply) & (flowpaths.df['pzm'] == roomid) ]) < 1):
            print("There is no mechanical supply device in room ",rooms.loc[roomid,'name'])
            print("Check failed")
            exit()
       
    
    
    
    
    
    #-----------------------------------------------------
    #Checking the number of connections between each room
    #-----------------------------------------------------
    
    room_pairs=list(itertools.combinations(list(rooms.index),2))  #unique pairs
    
    # Room - Room paths
    
    for roomid1,roomid2 in room_pairs:
    
        commonflowpaths=contam_functions.getcommonpaths(flowpaths,roomid1,roomid2)    
        df=commonflowpaths.copy()  #name change for concision
    
        #print(zones.df.loc[roomid1,'name'],zones.df.loc[roomid2,'name'])
        #print(df)
        #input('...')
       
        if ( -1 not in [roomid1,roomid2]):  # -1 is 'ext'  --> only check paths between rooms
        
            if ( rooms.loc[roomid1,'pl'] == rooms.loc[roomid2,'pl']  ):  #zones on same level
           
                if ( len(commonflowpaths) > 0 and len(commonflowpaths) !=4 ):
                    print("")
                    print("Wrong number of flow paths between ",rooms.loc[roomid1,'name'],"and",rooms.loc[roomid2,'name'],".")
                    print("There should be 4 (or zero) connections between spaces in the same level")
                    print("")
                    print(commonflowpaths)
                    print("")
                    exit()
    
            else:
                if ( len(commonflowpaths) > 0 and len(commonflowpaths) !=4 ):
                
                    if (3 in commonflowpaths['dir'].values or 6 in commonflowpaths['dir'].values):  #3 or 6 are vertical paths! 
                
                        print("Wrong number of flow paths between ",rooms.loc[roomid1,'name'],"and",rooms.loc[roomid2,'name'],". There should be FOUR VERTICAL connection between two spaces at different levels")
                        print("")
                        print(commonflowpaths)
                        exit()
    
                    elif (len(commonflowpaths) !=4):
                        
                        print("")
                        print("Wrong number of flow paths between ",rooms.loc[roomid1,'name'],"and",rooms.loc[roomid2,'name'],".")
                        print("There should be 4 (or zero) connections between spaces")
                        print(" WARNING : one of the zones is a 'phantom zone")
                        print("")
                        print(commonflowpaths)
                        print("")
                        exit()
    
    
    
    #-------------------------------------------------------------------------
    #Checking number of connection with outside and area file for infiltration
    #-------------------------------------------------------------------------
    
    areadf=pd.DataFrame(columns=['roomid','roomname','surface','wall-length','wall-height','area'])
    
    if (6 not in flowpaths.df['dir'].unique()):
        print("There is no leak towards the ground")
        exit()
        
    if (4 not in flowpaths.df['dir'].unique()):
        print("There is no lead towards the roof")
        exit()
    
    
    for roomid in rooms.index:  
        
        # filter by direction on the skethcpad  1,2,3,4,5,6  --> 3 and 6 are vertical paths
        # other:  dir 4 --> az=0 ; dir 5 : az=90 ; dir 2: az=270  ; dir 1: az=180
        sketchdirs={1:'S',2:'W',4:'N',5:'E'}
      
          
        commonflowpaths=contam_functions.getcommonpaths(flowpaths,roomid,-1) #-1 is zone id in flow paths for outside    
        df=commonflowpaths.copy()  #name change for concision
    
    
        areadf=areadf.append({'roomid':roomid,'roomname':rooms.loc[roomid,'name'],'surface':'floor-area','area':np.nan,'wall-height':'-','wall-length':'-'},ignore_index=True)
           
           
        for direction in df['dir'].unique():
    
            npaths=df[df['dir']==direction]['dir'].count()
    
            if direction in [3,6]:  #up or down
            
                if (npaths != 1):
                    print("")
                    print("Wrong number of flow paths between ",rooms.loc[roomid,'name'],"and exterior on facade ",sketchdirs[direction])
                    print("There should be 1 connnection, while there are ",npaths)
                    print("")
                    exit
                    
                else:
                    fpindex=df.index[df['dir']==direction][0]
                    if (df.loc[fpindex,'pld'] > rooms.loc[roomid,'pl'] ):  #junction start for level higher --> roof
                        areadf=areadf.append({'roomid':roomid,'roomname':rooms.loc[roomid,'name'],'surface':'facade-roof','wall-length':'-','wall-height':'-','area':np.nan},ignore_index=True)
                    else:
                        areadf=areadf.append({'roomid':roomid,'roomname':rooms.loc[roomid,'name'],'surface':'facade-ground','wall-length':'-','wall-height':'-','area':np.nan},ignore_index=True)
            
            else: # N,S,E,W
                
                if (npaths != 4):
                    print("")
                    print("Wrong number of flow paths between ",rooms.loc[roomid,'name'],"and exterior on facade ",sketchdirs[direction])
                    print("There should be 4 connnections, while there are ",npaths)
                    print("")
                    exit
                else:
                
                   areadf=areadf.append({'roomid':roomid,'roomname':rooms.loc[roomid,'name'],'surface':'facade-'+sketchdirs[direction],'wall-length':np.nan,'wall-height':3.0,'area':np.nan},ignore_index=True)
    
    areadf.index=areadf['roomid']
    areadf.drop(['roomid'],axis=1,inplace=True)
    areadf.sort_values(by=['surface'],inplace=True)
    
    areadf.to_csv(root+'-areas-empty.csv')
    #print(areadf)
    
    print("Check successfull")



if __name__=='__main__':
    
    fname = sys.argv[1]

    checkContamPlan(fname)


