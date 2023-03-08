
import pandas as pd
import numpy as np
import copy
   
    
def compute(args):
  
    #------------------
    # Read CONTAM model
    #------------------
    #contam_data=contam_functions.loadcontamfile(contamfile)
    contam_data=copy.deepcopy(args[0])
    zones=contam_data['zones']
    flowpaths=contam_data['flowpaths']

    #----------------------------
    # DICTIONNARY TO WRITE DOWN
    #----------------------------
    jsonDict={'Mechanical supply':[],
              'Mechanical exhaust':[],
              'Natural supply':[],
              'Natural exhaust':[],
              'Natural transfer':[]
              }


    assignZoneTypes(zones)      # Defining if zones are wet or dry

    computeExtractionsAndSupplys(zones,jsonDict)  # Compute flow rate or vent capacities for each space
    defineNaturalTransfers(zones,flowpaths,jsonDict) #Define natural transfers
    
    return jsonDict



def computeFlow(area,function):

    #----------------------------------------------------------
    # Defining types (wet/dry/hal) for different kind of spaces
    #----------------------------------------------------------
    wet=['Wasplaats','Badkamer','WC','Keuken','OKeuken']  # types of wet spaces
    dry=['Slaapkamer','Woonkamer','Bureau','Speelkamer']  # types of dry spaces
    hal=['hal','Hal','Garage','Berging','Dressing']       # others 


    # -------------------------------------
    # Flow rate rules based on NBN-D-50-001
    # -------------------------------------

    #general rule
    flow = 3.6 * area  

    #applying bounds for different types of spaces
    spacesbounds=pd.DataFrame(columns=['min','max','fixed'],index=dry+wet)

    spacesbounds.loc['WC',:]=25
    spacesbounds.loc['Badkamer',:]=[50,np.nan,np.nan]
    spacesbounds.loc['Keuken',:]=[50,75,np.nan]
    spacesbounds.loc['OKeuken',:]=[75,75,np.nan]

    spacesbounds.loc['Wasplaats',:]=[50,np.nan,np.nan]
    spacesbounds.loc['Slaapkamer',:]=[25,72,np.nan]
    spacesbounds.loc['Woonkamer',:]=[75,150,np.nan]
    spacesbounds.loc['Bureau',:]=[25,36,np.nan]

    
    if (flow > spacesbounds.loc[function,'max']):
        newflow=spacesbounds.loc[function,'max']

    elif (flow < spacesbounds.loc[function,'min']):
        newflow=spacesbounds.loc[function,'min']

    else:
        newflow=flow

    return newflow


def assignZoneTypes(zones):

    #----------------------------------------------------------
    # Defining types (wet/dry/hal) for different kind of spaces
    #----------------------------------------------------------
    wet=['Wasplaats','Badkamer','WC','Keuken','OKeuken']  # types of wet spaces
    dry=['Slaapkamer','Woonkamer','Bureau','Speelkamer']  # types of dry spaces
    hal=['hal','Hal','Garage','Berging','Dressing']       # others 


    # ----------------------------------------------
    # Assingning types and functions to model spaces
    # ----------------------------------------------
    for zoneindex in zones.df.index:
        
        zonename=zones.df.loc[zoneindex,'name']
        
        for zonetype in wet:
            if (zonetype in zonename):
            # create exhaust, natural of mechanical
                zones.df.loc[zoneindex,'type']='wet'
                zones.df.loc[zoneindex,'function']=zonetype

        for zonetype in dry:
            if (zonetype in zonename):
            # create exhaust, natural of mechanical
                zones.df.loc[zoneindex,'type']='dry'
                zones.df.loc[zoneindex,'function']=zonetype

        for zonetype in hal:
            if (zonetype in zonename):
            # create exhaust, natural of mechanical
                zones.df.loc[zoneindex,'type']='hal'
                zones.df.loc[zoneindex,'function']='hal'


def computeExtractionsAndSupplys(zones,jsondict):


    numberOfZones = len(zones.df[zones.df['flags']==3])


    for zoneindex in zones.df.index:
        
        if (zones.df.loc[zoneindex,'flags'] != 3):
            #ignore AHS
            continue 
        
        area=float(zones.df.loc[zoneindex,'Vol'])/3.0

        #print(zones.df.loc[zoneindex,'name'])

        # mechanical extraction: C & D
        if (zones.df.loc[zoneindex,'type'] in ['wet']):
            
            function=zones.df.loc[zoneindex,'function']
            
            flow=computeFlow(area,zones.df.loc[zoneindex,'function'])
            
            MEdict={'Room':zones.df.loc[zoneindex,'name'],'Nominal flow rate':flow}
            jsondict['Mechanical exhaust'].append(MEdict)

        if (numberOfZones==1):
            
            MEdict={'Room':zones.df.loc[zoneindex,'name'],'Nominal flow rate':75}
            jsondict['Mechanical exhaust'].append(MEdict)            

        if (zones.df.loc[zoneindex,'type'] in ['dry']):
        
            flow=computeFlow(3.6*area,zones.df.loc[zoneindex,'function'])
            NSdict={'Room':zones.df.loc[zoneindex,'name'],'Capacity':flow,'Design pressure':2,'Self-Regulating':'No'}
            jsondict['Natural supply'].append(NSdict)



def defineNaturalTransfers(zones,flowpaths,jsondict):

    for fp in flowpaths.df.index:

        fromzid=int(flowpaths.df.loc[fp,'pzn'])
        tozid=int(flowpaths.df.loc[fp,'pzm'])
        
        if ( -1 not in [fromzid,tozid]):
            
            fromtype=zones.df.loc[fromzid,'type']
            totype=zones.df.loc[tozid,'type']
        
            # Natural transfer between two adjacent spaces of different type
            # OR natural transfer between two 'hal' types
            
            if ( (fromtype!=totype and fromtype in ['wet','dry','hal'] and totype in ['wet','dry','hal']) or (fromtype=='hal' and totype=='hal') ): 
            
                if ('OKeuken' in [zones.df.loc[fromzid,'name'],zones.df.loc[tozid,'name']] and 'Woonkamer' in [zones.df.loc[fromzid,'name'],zones.df.loc[tozid,'name']]):
                    continue
            
                NTdict={'From room':zones.df.loc[fromzid,'name'],
                        'To room':zones.df.loc[tozid,'name'],
                        'Capacity':25,
                        'Design pressure':2
                        }
            
                if (NTdict not in jsondict['Natural transfer']):
            
                    jsondict['Natural transfer'].append(NTdict)
                


