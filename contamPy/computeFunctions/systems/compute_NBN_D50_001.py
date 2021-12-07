
import pandas as pd
import numpy as np
import copy
   
    
def compute(args):

    contam_data=copy.deepcopy(args[0])
    system=args[1]
     
    if (system not in ['A','B','C','D']):
        print("")
        print("System ",system," does not exist")
        print("Valid systems are A,B,C or D")
        print("")
        exit()


    autobalancehal=False
    autobalanceprop=False
    if (system == 'D' and len(args)>2):

        if ( args[2] == 'auto-balance-hal' ):
            autobalancehal=True
        if ( args[2] == 'auto-balance-prop' ):
            autobalanceprop=True


    addExtractSlaapkamers=False
    if (system == 'C' and len(args)>2):

        if ( args[2] == 'extract-slaapkamers' ):
            addExtractSlaapkamers=True

    #system='D'
    #system='C'


    #--------------------------------------------
    # Defining types (wet/dry/hal) and functions
    #--------------------------------------------
    wet=['Wasplaats','Badkamer','WC','Keuken','OKeuken']  # existing functions in dry spaces
    dry=['Slaapkamer','Woonkamer','Bureau','Speelkamer']  # existing function in wet spaces
    hal=['hal','Hal','Garage','Berging','Dressing'] #existing functions for hal



    # -------------------------------------
    # Flow rate rules based on NBN-D-50-001
    # -------------------------------------
    def boundflow(flow,function):

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


    #------------------
    # Read CONTAM model
    #------------------
    #contam_data=contam_functions.loadcontamfile(contamfile)
    zones=contam_data['zones']
    flowpaths=contam_data['flowpaths']


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



    #----------------------------
    # DICTIONNARY TO WRITE DOWN
    #----------------------------
    jsondict={'Mechanical supply':[],
              'Mechanical exhaust':[],
              'Natural supply':[],
              'Natural exhaust':[],
              'Natural transfer':[]
              }

    totalsup=0.
    totalexh=0.


    numberOfZones = len(zones.df[zones.df['flags']==3])
                
         
    # ----------------------------
    # Defining supply and extract
    # ----------------------------
    for zoneindex in zones.df.index:
        
        if (zones.df.loc[zoneindex,'flags'] != 3):
            #ignore AHS
            continue 
        
        area=float(zones.df.loc[zoneindex,'Vol'])/3.0

        #print(zones.df.loc[zoneindex,'name'])

        # mechanical extraction: C & D
        if (system in ['C','D'] and zones.df.loc[zoneindex,'type'] in ['wet']):
            
            function=zones.df.loc[zoneindex,'function']
            
            flow=boundflow(3.6*area,zones.df.loc[zoneindex,'function'])
            
            MEdict={'Room':zones.df.loc[zoneindex,'name'],'Nominal flow rate':flow}
            jsondict['Mechanical exhaust'].append(MEdict)
         
            totalexh+=flow

        if (addExtractSlaapkamers and system == 'C' and 'Slaap' in zones.df.loc[zoneindex,'name']):
            
            flow=30
            MEdict={'Room':zones.df.loc[zoneindex,'name'],'Nominal flow rate':flow}
            jsondict['Mechanical exhaust'].append(MEdict)
        
            totalexh+=flow

        if (numberOfZones==1 and system =='C'):
            
            MEdict={'Room':zones.df.loc[zoneindex,'name'],'Nominal flow rate':75}
            jsondict['Mechanical exhaust'].append(MEdict)            
         
        if (system in ['B','D'] and zones.df.loc[zoneindex,'type'] in ['dry']):

            flow=boundflow(3.6*area,zones.df.loc[zoneindex,'function'])
            
            MSdict={'Room':zones.df.loc[zoneindex,'name'],'Nominal flow rate':flow}
            jsondict['Mechanical supply'].append(MSdict)
            
            totalsup+=flow
            

        if (system in ['A','C'] and zones.df.loc[zoneindex,'type'] in ['dry']):
        
            flow=boundflow(3.6*area,zones.df.loc[zoneindex,'function'])
            NSdict={'Room':zones.df.loc[zoneindex,'name'],'Capacity':flow,'Design pressure':2,'Self-Regulating':'No'}
            jsondict['Natural supply'].append(NSdict)


    # BALANCE
    #-----------

    imbalance=abs(totalsup-totalexh)

    if imbalance > 1.0:
        balance=False
    else:
        balance = True

    while (system=='D' and not balance):

        imbalance=totalsup-totalexh

        if (autobalancehal):
            print("Imbalance: ",imbalance," m3/h (supply:",totalsup,"m3/h, exhaust:",totalexh,"m3/h)")
            print("Automatic balancing")
            halzonesindex=zones.df[zones.df['type']=='hal'].index
            
            nhal=len(halzonesindex)

            if (nhal>0):
                for zoneid in halzonesindex:
                    MEdict={'Room':zones.df.loc[zoneid,'name'],'Nominal flow rate':abs(imbalance)/nhal}
                    jsondict['Mechanical exhaust'].append(MEdict)
                totalexh+=abs(imbalance)

                break

            else:
                print("No hall to add additional extractions, increasing proportionally in wet spaces")
                autobalanceprop=True
            
        
        if (autobalanceprop):

            if (totalexh != 0):            
                factor=totalsup/totalexh
                
                for MEdict in jsondict['Mechanical exhaust']:
                    MEdict['Nominal flow rate']=MEdict['Nominal flow rate']*factor
                    
            else:
                print("No existing extraction")
                
                if numberOfZones == 1 :
                    print("Only one zone")
                    zoneName = zones.df[zones.df['flags']==3]['name'].iloc[0]
                    MEdict={'Room':zoneName,'Nominal flow rate':totalsup}
                    jsondict['Mechanical exhaust'].append(MEdict)
                
                else:
                    print("Impossible case")
                    return
                
            break

        """print("")
        print("WARNING: the system is unbalanced !")
        print("")
        print("Imbalance: ",totalsup-totalexh," m3/h (supply:",totalsup,"m3/h, exhaust:",totalexh,"m3/h)")
        print("")
        """
        
        if (totalsup > totalexh) : # most common case
            
            #Adding extra exhaust in hal or dry spaces
            
            extraexh=input("Add extra exhaust in hal of dry spaces (y/n) ? ")
            
            if (extraexh in ['y','Y']):
            
                print(zones.df[ (zones.df['type']=='hal') | (zones.df['type']=='dry')]['name'].to_string())
            
                ids=input("Select rooms in which to add an exhaust (room nr seperated with commas, e.g. 1,2,3 ) :  " )
            
                for roomid in [ int(x) for x in ids.split(',')]:
            
            
                    flow=float(input("Nominal flow rate for extract in room "+str(zones.df.loc[roomid,'name'])+' : '))

                    MEdict={'Room':zones.df.loc[roomid,'name'],'Nominal flow rate':flow}
                    jsondict['Mechanical exhaust'].append(MEdict)
                
                    totalexh+=flow
                
                    print("")
                    print("Imbalance: ",totalsup-totalexh," m3/h (supply:",totalsup,"m3/h, exhaust:",totalexh,"m3/h)")
                    print("")
     

            changeflowrate=input("Change flow rate of existing extractions ? (y/n) ")
        
            if (changeflowrate in ['y','Y']):

                print('{:3}'.format('id'), '{:12}'.format('Room'), '{:10}'.format('Flow rate') )
                
                for item in jsondict['Mechanical exhaust']:
                
                    roomid=zones.df[zones.df['name']==item['Room']].index[0]
                
                    print('{:3}'.format(str(roomid)), '{:12}'.format(item['Room']), '{:10}'.format(str(item['Nominal flow rate'])))

                ids=input("Choose rooms for wich to change the flow rate (roomid, separated by commas, e.g. 1,2,3) :  " )
                    
                for roomid in [ int(x) for x in ids.split()]:

                    flow=float(input("New flow rate for extract in room "+str(zones.df.loc[roomid,'name'])+' : '))

                    roomname=zones.df.loc[roomid,'name']
                    
                    for item in jsondict['Mechanical exhaust']:
                        if (item['Room']==roomname):
                            totalexh+= -item['Nominal flow rate']
                            item['Nominal flow rate']=flow
                            totalexh+= item['Nominal flow rate']
                            
                            print("")
                            print("Imbalance: ",totalsup-totalexh," m3/h (supply:",totalsup,"m3/h, exhaust:",totalexh,"m3/h)")
                            print("")
        #print("Dry spaces")
        #print(zones.df[zones.df['type']=='dry']['name'].to_string())
        
        
        #if (totalsup > totalexh) : # most common case
        
        

        if ( abs(totalsup - totalexh) > 1):
            balance=False
        else:
            print("")
            print("Sufficient balance (<1 m3/h) is reached")
            print("")
            balance=True

    #-----------------------------
    # Defining natural transfers
    #----------------------------- 

    for fp in flowpaths.df.index:

        fromzid=int(flowpaths.df.loc[fp,'pzn'])
        tozid=int(flowpaths.df.loc[fp,'pzm'])
        
        if ( -1 not in [fromzid,tozid]):
            
            fromtype=zones.df.loc[fromzid,'type']
            totype=zones.df.loc[tozid,'type']
                 
            #print(fp,zones.df.loc[fromzid,'name'],fromtype,zones.df.loc[tozid,'name'],totype)
        
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
                

    return jsondict


