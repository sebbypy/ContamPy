
import contam_functions
import pandas as pd
import copy
 
    
def compute(**kwargs):

    inputSystemJson = kwargs['systemJSON']
    contam_data = kwargs['contamModel']

    contamModel=copy.deepcopy(contam_data) #working on a copy, don't have to modify it
    outputSystemJson = inputSystemJson.copy()


    #--------------------------------------------
    # Defining types (wet/dry/hal) and functions
    #--------------------------------------------
    wet=['Wasplaats','Badkamer','WC','Keuken','OKeuken']  # existing functions in dry spaces
    dry=['Slaapkamer','Woonkamer','Bureau','Speelkamer']  # existing function in wet spaces
    hal=['hal','Hal']                                     # existing functions for hal
    others=['Garage','Berging','Dressing']                # other functions



    # -----------------------------------------------
    # Flow rate rules based on PREVENT experience
    # -----------------------------------------------
    def computeflow(function,biggestbedroom,nbedrooms):

        flowdict={'WC':25,
              'Badkamer':50,
              'Keuken':50,
              'OKeuken':50,
              'Wasplaats':50,
              'Slaapkamer':25,
              'Woonkamer':25*(nbedrooms+1),
              'Bureau':25
              }

        flow=flowdict[function]
        
        
        if (biggestbedroom):
            flow=flow*2

        return flow


    #------------------
    # Read CONTAM model
    #------------------
    zones=contamModel['zones']
    flowpaths=contamModel['flowpaths']

 
    openDoors=[]
        

    for zoneindex in zones.df.index:
        
        zonename=zones.df.loc[zoneindex,'name']
        
        for zonetype in wet:
            if (zonetype in zonename):
                zones.df.loc[zoneindex,'type']='wet'
                zones.df.loc[zoneindex,'function']=zonetype

        for zonetype in dry:
            if (zonetype in zonename):
                zones.df.loc[zoneindex,'type']='dry'
                zones.df.loc[zoneindex,'function']=zonetype
                

        for zonetype in hal:
            if (zonetype in zonename):
                zones.df.loc[zoneindex,'type']='hal'
                zones.df.loc[zoneindex,'function']='hal'

        for zonetype in others:
            if (zonetype in zonename):
                zones.df.loc[zoneindex,'type']='other'
                zones.df.loc[zoneindex,'function']='other'


    
    for fromZoneId in zones.df.index:
 
        fromZoneName = zones.df.loc[fromZoneId,'name']
        fromZoneType = zones.df.loc[fromZoneId,'type']
        
        for toZoneId in zones.df.index:

            doorDict={}
            
            toZoneName = zones.df.loc[toZoneId,'name']
            toZoneType = zones.df.loc[toZoneId,'type']
               
            commonflowpaths=contam_functions.getcommonpaths(flowpaths,fromZoneId,toZoneId)    
            
            if ( len(commonflowpaths)>0 and fromZoneType == 'dry' and toZoneType == 'hal'):
                
                doorDict={'From room':fromZoneName,
                          'To room':toZoneName}   
    
    
            if ( len(commonflowpaths)>0 and fromZoneName in ['Keuken','OKeuken'] and toZoneType == 'hal'):
    
                doorDict={'From room':fromZoneName,
                          'To room':toZoneName}   

                
            if ( len(commonflowpaths)>0 and fromZoneName in ['Keuken','OKeuken'] and toZoneType == 'dry'):
    
                doorDict={'From room':fromZoneName,
                          'To room':toZoneName}   


            if (len(doorDict) > 0):
                
                openDoors.append(doorDict)



        outputSystemJson['Open doors'] = openDoors
     


    return outputSystemJson
