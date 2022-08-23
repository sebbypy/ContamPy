import sys
import os

dirPath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dirPath,'..','contamFunctions'))


import contam_functions
import numpy as np
import pandas as pd
import itertools



def setContamPlan(inputFileName,csvFileNameWithPath,outputFileNameWithPath):

    
    
    azimuthdict={0:'N',180:'S',90:'E',270:'W'}
    directiondict={3:'ground',6:'roof'}
    
    #------------------
    # Load CONTAM FILE
    #------------------
    
    contam_data=contam_functions.loadcontamfile(inputFileName)
    
    # Extract different sections
    levels=contam_data['levels']
    zones=contam_data['zones']
    flowpaths=contam_data['flowpaths']
    flowelems=contam_data['flowelems']
    contaminants=contam_data['contaminants']
    ahs=contam_data['ahs']
    controls=contam_data['controls']
    wprofiles=contam_data['windprofiles']
    
    #--------------------------------------------
    # Getting the ID of the generic flow elements
    #--------------------------------------------
    defaultelem=flowelems.df[flowelems.df['name']=='DefaultPath'].index[0]
    crackelemid=flowelems.df[flowelems.df['name']=='Gen_crack'].index[0]
    nat_supply_id=flowelems.df[flowelems.df['name']=='Gen_NSV'].index[0]
    nat_transfer_id=flowelems.df[flowelems.df['name']=='Gen_NT'].index[0]
    constant_flow_id=flowelems.df[flowelems.df['name']=='ConstantFlow'].index[0]
    large_opening_id=flowelems.df[flowelems.df['name']=='LargeOpening'].index[0]
    
    #----------------------------------------------------
    # Getting ID of AHS zones (to be treated differently)
    # ---------------------------------------------------
    AHSreturn=ahs.df.loc[1,'zr#']
    AHSsupply=ahs.df.loc[1,'zs#']
    
    #-----------------------
    #Getting areas from file
    #-----------------------
    #areas=pd.read_csv(rootwithpath+'-areas-filled.csv',index_col=0,na_values=['-']) #interpret "-" as NaN so that other lines are read as float
    areas=pd.read_csv(csvFileNameWithPath,index_col=0,na_values=['-']) #interpret "-" as NaN so that other lines are read as float
 
    areas.loc[areas['area'].isna(),'area']=areas.loc[areas['area'].isna(),'wall-length']*areas.loc[areas['area'].isna(),'wall-height']
    
    
    
    #-------------------------------------------------
    # Setting volume of zones (depending on floor area)
    #-------------------------------------------------
    
    #print(zones.df)
    #print(areas)
    #print(areas[areas['surface']=='floor-area'])
    
    for zid in zones.df.index:
        if zid in areas.index:
            zones.df.loc[zid,'Vol']=areas[areas['surface']=='floor-area'].loc[zid,'area']*3
    
    
    # -------------------------------------------------
    # Defining wall areas for infiltration calculations
    # -------------------------------------------------
    
    for room in areas['roomname'].unique():
    
        zoneid=zones.df[zones.df['name']==room].index[0]
    
        #Retain only those in contact with ext
        zonepaths=flowpaths.df[(flowpaths.df['pzn']==-1) & (flowpaths.df['pzm']==zoneid)]
    
        for azimuth in zonepaths['wazm'].unique():
        
            dirpaths=zonepaths[ (zonepaths['wazm']==azimuth) & (zonepaths['dir'].isin([1,2,4,5]) ) ] # 'dir' in '1,2,4,5' = horizontal connections
               
            if (int(azimuth) < 0 or len(dirpaths)==0):
                continue
    
            facade=azimuthdict[int(azimuth)]
            
            area=areas[ (areas['roomname']==room) & (areas['surface']=='facade-'+facade) ]['area']
            area=areas[ (areas['roomname']==room) & (areas['surface']=='facade-'+facade) ]['area'].iloc[0]
                
            for i in range(len(dirpaths)):
                #only target the two first of the list that are devoted to infiltrations
                
                if (i<2):
                 
                    boundary = areas[ (areas['roomname']==room) & (areas['surface']=='facade-'+facade) ]['boundary'].iloc[0]
                    
                    index=dirpaths.index[i]
                    flowpaths.df.loc[index,'mult']=area/2
                    flowpaths.df.loc[index,'pe']=crackelemid
    
                    if (i==0):
                        flowpaths.df.loc[index,'relHt']=0.65
                    else:
                        flowpaths.df.loc[index,'relHt']=1.85
                        
                    if boundary == 'vertical-outside':
                        flowpaths.df.loc[index,'flags']=1
                        flowpaths.df.loc[index,'pw']=wprofiles.df[wprofiles.df['name'].str.contains('Wall')].index[0]
                    elif boundary == 'zero-pressure':
                        #doing nothign
                        pass
                    else:
                        print("Error : for vertical facades, the only acceptable boundary conditions are 'vertical-outside' or 'zero-pressure'")
                        return

                
                if (i==2): #i==2 --> 3rd in the list
                    index=dirpaths.index[i]
                    flowpaths.df.loc[index,'pe']=nat_supply_id
    
    
                    #by default, natural supply vents are assumed on walls... Maybe has to be changed later ? 
                    flowpaths.df.loc[index,'flags']=1
                    flowpaths.df.loc[index,'pw']=wprofiles.df[wprofiles.df['name'].str.contains('Wall')].index[0]

                    """elif boundary == 'zero-pressure':
                        #doing nothign
                        pass
                    else:
                        print("Error : for natural supply vents, the only acceptable boundary conditions are 'vertical-outside' or 'zero-pressure'")
                        return
                    """ 
                
    
                if (i==4):
                             
                    area=areas[ (areas['roomname']==room) & (areas['surface']=='facade-slopedroof') ]['area'].iloc[0]

                    #should only be sloped-outside
                    boundary = areas[ (areas['roomname']==room) & (areas['surface']=='facade-slopedroof') ]['boundary'].iloc[0]
                    
                    print("boundary ",boundary)
                    
                    index=dirpaths.index[4]
                    flowpaths.df.loc[index,'pe']=crackelemid
                    flowpaths.df.loc[index,'mult']=area
                    
                    flowpaths.df.loc[index,'flags']=1
                    
                    if boundary == 'sloped-outside':
                        flowpaths.df.loc[index,'pw']=wprofiles.df[wprofiles.df['name'].str.contains('30')].index[0] # roof > 30 degrees profile
                    else:
                        print("Unconsistent boundary condition : slopedroof facade should only have sloped-outside boundary conditioné")
                        print("Otherwise this fifth path, it should not exist")
                        return
    
    
        for pathdir in [3,6]:
        
            dirpaths=zonepaths[zonepaths['dir']==pathdir]
     
            if (not dirpaths.empty):
            
                area=areas[ (areas['roomname']==room) & (areas['surface']=='facade-'+directiondict[pathdir]) ]['area']
                area=area.iloc[0]
    
                index=dirpaths.index[0] # theoritically, there should be only one line in this one (if the model is ok, i.e. if there is only one path above or below

                boundary = areas[ (areas['roomname']==room) & (areas['surface']=='facade-'+directiondict[pathdir]) ]['boundary'].iloc[0]

                
                flowpaths.df.loc[index,'pe']=crackelemid
                flowpaths.df.loc[index,'mult']=area

                if boundary == 'flat-outside':    
                    flowpaths.df.loc[index,'flags']=1
                    flowpaths.df.loc[index,'pw']=wprofiles.df[wprofiles.df['name'].str.contains('Flat')].index[0] #flat roof profile

                elif boundary == 'zero-pressure':
                    print("Zero pressure boundary, doing nothing")

                else:
                    print("Only valid boundaries are flat-outside ad zero-pressure")
                    return
    
    #-------------------------------------------------------------
    # Defining Natural transfers openings (default at 0.25 m high)
    #-------------------------------------------------------------
    
    room_pairs=list(itertools.combinations(list(zones.df.index),2))  #unique pairs
    
    for roomid1,roomid2 in room_pairs:
        
        commonflowpaths=contam_functions.getcommonpaths(flowpaths,roomid1,roomid2)    
    
        roomname1=zones.df.loc[roomid1,'name']
        roomname2=zones.df.loc[roomid2,'name']
    
        if (not commonflowpaths.empty) and  not any([x in [AHSreturn,AHSsupply] for x in [roomid1,roomid2] ] ) :
    
            for i in range(len(commonflowpaths)):
                
                index=commonflowpaths.index[i]
            
                if ('OKeuken' in [roomname1,roomname2] and 'Woonkamer' in [roomname1,roomname2]):
                   
                    if (i==1):
                        flowpaths.df.loc[index,'pe']=large_opening_id
                        flowpaths.df.loc[index,'relHt']=0.25
                        flowpaths.df.loc[index,'mult']=1
                                       
                    if (i==2):
                        flowpaths.df.loc[index,'pe']=constant_flow_id
                        flowpaths.df.loc[index,'relHt']=0.25
                        flowpaths.df.loc[index,'mult']=1
    
                    if (i==3): #reverse
                        flowpaths.df.loc[index,'pe']=constant_flow_id
                        flowpaths.df.loc[index,'relHt']=0.25
                        contam_functions.reversepath(flowpaths,index)
                        flowpaths.df.loc[index,'mult']=1
    
                else:
                    if (i==1):
                        flowpaths.df.loc[index,'pe']=large_opening_id
                        flowpaths.df.loc[index,'relHt']=1.0
                        flowpaths.df.loc[index,'mult']=0
    
    
            
                if (i==0):
                    flowpaths.df.loc[index,'pe']=nat_transfer_id
                    flowpaths.df.loc[index,'relHt']=0.25
    
    
    
    #should probably be done in a latter stage
    
    #--------------------------------------------------
    # Adding species sensors (+log report) in each room
    #--------------------------------------------------
    
    for zoneid in zones.df.index:
        
        if ('AHS' in zones.df.loc[zoneid,'name']):
            continue
    
        for specie in contaminants.df['name']:
        
            if ('WC' in specie):
                continue
        
            #addspeciesensor(self,zonesdf,roomid,specie_name,name,description='')
            controls.addspeciesensor(zones.df,zoneid,specie,specie+'-sensor') #add sensor and report directly
    
    
        controls.addoccupancysensor(zones.df,zoneid,'occ-sensor') 
    
    
    #----------------------------------------------------------
    # Adding controls + flow sensors and reports for MS, ME, NS 
    #----------------------------------------------------------
    
    for index in flowpaths.df.index:
        
        fromto=list(flowpaths.df.loc[index,['pzm','pzn']])
            
        if AHSreturn in fromto:
            fromto.remove(AHSreturn)
            otherzone=fromto[0]
            if (otherzone not in [-1,AHSsupply]):
            
                controls.addconstant('C_ME_'+str(zones.df.loc[otherzone,'name']),1)
                flowpaths.df.loc[index,'pc']=controls.df.index[-1]
    
                controls.addflowsensor(index,'Q_ME_'+str(zones.df.loc[otherzone,'name']))
    
        fromto=list(flowpaths.df.loc[index,['pzm','pzn']])
            
        if AHSsupply in fromto:
            fromto.remove(AHSsupply)
            otherzone=fromto[0]
            if (otherzone not in [-1,AHSreturn]):
                controls.addconstant('C_MS_'+str(zones.df.loc[int(otherzone),'name']),1)
                flowpaths.df.loc[index,'pc']=controls.df.index[-1]
    
                #addflowensor(self,flowpathdf,pathid,,name,description=''):
                controls.addflowsensor(index,'Q_MS_'+str(zones.df.loc[otherzone,'name']))
    
    
        if flowpaths.df.loc[index,'pe']==nat_supply_id:
            #addding control_variable to natural supply vents
    
            fromto=list(flowpaths.df.loc[index,['pzm','pzn']])
            fromto.remove(-1)
            otherzone=fromto[0]
    
            controls.addconstant('C_NS_'+str(zones.df.loc[int(otherzone),'name']),1)
            flowpaths.df.loc[index,'pc']=controls.df.index[-1]
     
            #print('flow path '+str(index)+' adding natural supply for room '+str(zones.df.loc[int(otherzone),'name']))
            
            #addflowensor(self,flowpathdf,pathid,,name,description=''):
            controls.addflowsensor(index,'Q_NS_'+str(zones.df.loc[otherzone,'name']))
    
    
    #----------------------------------------------------------------------------------------------------------------
    # Setting multiplier to 0 for each of the generic flow paths but the cracks AND fans that are used to mix Okeuken
    #----------------------------------------------------------------------------------------------------------------
    
    for index in flowpaths.df.index:
    
        #if flowpaths.df.loc[index,'pe']==defaultelem:
        if (flowpaths.df.loc[index,'pe'] not in [crackelemid,constant_flow_id,large_opening_id] ):
            flowpaths.df.loc[index,'mult']=0.0
    
  
    
    contam_functions.writecontamfile(inputFileName,outputFileNameWithPath,contam_data)
    
    print("File "+outputFileNameWithPath+" with areas generated")
    
    



if __name__ == '__main__':
    

    if (len(sys.argv) <2 ):
        print("Usage: ")
        print("")
        print("     python3 set-contam-plan.py contam.prj")
        print("")
        exit()

    inputFileName=sys.argv[1]

    rootwithpath=inputFileName.replace('.prj','')
    root=os.path.basename(inputFileName).replace('.prj','')  # name of contam file without path and without extension

    
    csvFileNameWithPath = rootwithpath+'-areas-filled.csv'
    
    setdir = os.path.join(os.getcwd(),'2-DimBuildings')
    
    outputFileNameWithPath = os.path.join(setdir,root+'.prj')
   
    setContamPlan(inputFileName,csvFileNameWithPath,outputFileNameWithPath)
    
    exit()

