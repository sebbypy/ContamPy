
import contam_functions
import pandas as pd
import copy


def writetolog(string):
    
    fileName = '.computePREVENTLog'
    
    f = open(fileName,'a')
    f.write(string+'\n')
    f.close
        


 
    
def compute(args):

    contam_data=copy.deepcopy(args[0])
    system=args[1]

    checkArguments(system)

    
    autobalancehal=False
    autobalanceprop=False
    if (system in ['C','D','DRecyclage','CRecyclage'] and len(args)>2):

        if ( args[2] == 'auto-balance-hal' ):
            autobalancehal=True
        if ( args[2] == 'auto-balance-prop' ):
            autobalanceprop=True


    if len(args)>3:
        supplyPressure = int(args[3])
    else:
        supplyPressure = 2


    zones=contam_data['zones']
    flowpaths=contam_data['flowpaths']
    flowelems=contam_data['flowelems']

    biggestbedroom,nbedrooms,numberOfZones = assignZoneTypesAndFunctions(zones,flowpaths)

    jsondict,totalsup,totalexh = setRequiredFlowRates(zones,biggestbedroom,system,numberOfZones,nbedrooms,supplyPressure)

    supplyAndExhaustBalancing(jsondict,system,zones,totalsup,totalexh,autobalancehal,autobalanceprop)

    jsonDict = balanceNaturalTransfers(zones,flowelems,flowpaths,jsondict)


    return jsonDict




def checkArguments(system):
    
    acceptablesystems=['A','B','C','D','CsupplyHall','CSLAAP','DRecyclage','CRecyclage']
     
    if (system not in acceptablesystems):
        writetolog("")
        writetolog("System ",system," does not exist")
        sysstring=''
        for s in acceptablesystems:
            sysstring+=s+' '
        writetolog("Valid systems are "+sysstring)
        writetolog("")
        exit()





def computeflow(function,biggestbedroom,nbedrooms):
    # -----------------------------------------------
    # Flow rate rules based on PREVENT experience
    # -----------------------------------------------

    flowdict={'WC':25,
          'Badkamer':50,
          'Douche':50,
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


def assignZoneTypesAndFunctions(zones,flowpaths):
    
    # ----------------------------------------------
    # Assingning types and functions to model spaces
    # ----------------------------------------------

    #--------------------------------------------
    # Defining types (wet/dry/hal) and functions
    #--------------------------------------------
    wet=['Wasplaats','Badkamer','WC','Keuken','OKeuken','Douche']  # existing functions in dry spaces
    dry=['Slaapkamer','Woonkamer','Bureau','Speelkamer']  # existing function in wet spaces
    hal=['hal','Hal']                                     # existing functions for hal
    others=['Garage','Berging','Dressing']                # other functions


    # Checking contact with outside

    #computing biggest bedroom (2 occupants)
    try:
        biggestbedroom=zones.df[zones.df['name'].str.contains('Slaapkamer')].sort_values(by='Vol',ascending=False)['name'].iloc[0]
    except:
        biggestbedroom=None
    nbedrooms=len(zones.df[zones.df['name'].str.contains('Slaapkamer')])

    numberOfZones = len(zones.df[zones.df['flags']==3])
 

    for zoneindex in zones.df.index:
        
        zonename=zones.df.loc[zoneindex,'name']

        

        if (zonename==biggestbedroom):
            zones.df.loc[zoneindex,'biggestbedroom']=True
        else:
            zones.df.loc[zoneindex,'biggestbedroom']=False
        
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

        for zonetype in others:
            if (zonetype in zonename):
            # create exhaust, natural of mechanical
                zones.df.loc[zoneindex,'type']='other'
                zones.df.loc[zoneindex,'function']='other'

        
        if (len(contam_functions.getcommonpaths(flowpaths,zoneindex,-1)) >= 4  ): # >=4 --> dans les modeles, il y a au moins 4 flowpahts vers l'exterieur. S'il n'y en a que 1, ca doit être sol ou plafond
            zones.df.loc[zoneindex,'outsideaccess']=True
        else:
            zones.df.loc[zoneindex,'outsideaccess']=False


    return biggestbedroom,nbedrooms,numberOfZones



def setRequiredFlowRates(zones,biggestbedroom,system,numberOfZones,nbedrooms,supplyPressure):

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

    
 
         
    # ----------------------------
    # Defining supply and extract
    # ----------------------------
    for zoneindex in zones.df.index:
        
        if (zones.df.loc[zoneindex,'flags'] != 3):
            #ignore AHS
            continue 

        boolbiggest=False
        if (zones.df.loc[zoneindex,'name']==biggestbedroom):
            boolbiggest=True

        # ME
        if (system in ['C','D','CRecyclage','DRecyclage'] and zones.df.loc[zoneindex,'type'] in ['wet']):
            
            function=zones.df.loc[zoneindex,'function']
            
            flow=computeflow(zones.df.loc[zoneindex,'function'],boolbiggest,nbedrooms)
            
            if (zones.df.loc[zoneindex,'name']=='OKeuken' and system in ['CRecyclage','DRecyclage']):
                flow = (nbedrooms+1)*25
            
            
            MEdict={'Room':zones.df.loc[zoneindex,'name'],'Nominal flow rate':flow}
            jsondict['Mechanical exhaust'].append(MEdict)
         
            
            totalexh+=flow

        if (system == 'CRecyclage' and zones.df.loc[zoneindex,'name']=='Woonkamer' and not zones.df['name'].isin(['OKeuken']).any()):
            
            flow = (nbedrooms+1)*25
            
            MEdict={'Room':zones.df.loc[zoneindex,'name'],'Nominal flow rate':flow}
            jsondict['Mechanical exhaust'].append(MEdict)
         
            totalexh+=flow

         
      
        if (numberOfZones==1 and system in ['C','D']):
 
            flow=75
            MEdict={'Room':zones.df.loc[zoneindex,'name'],'Nominal flow rate':flow}
            jsondict['Mechanical exhaust'].append(MEdict)            
            totalexh+=flow
            
            
        # Mechanical supply
        if (system in ['B','D','DRecyclage'] and zones.df.loc[zoneindex,'type'] in ['dry']):

            flow=computeflow(zones.df.loc[zoneindex,'function'],boolbiggest,nbedrooms)

            if system == 'DRecyclage' and zones.df.loc[zoneindex,'name']=='Woonkamer':
                pass
            else:
            
                MSdict={'Room':zones.df.loc[zoneindex,'name'],'Nominal flow rate':flow}
                jsondict['Mechanical supply'].append(MSdict)
                
                totalsup+=flow
            

        # NATURAL SUPPLY
        if (system in ['A','C','CSLAAP','CRecyclage'] and zones.df.loc[zoneindex,'type'] in ['dry']):
        
            flow=computeflow(zones.df.loc[zoneindex,'function'],boolbiggest,nbedrooms)

            if system == 'CRecyclage' and zones.df.loc[zoneindex,'name']=='Woonkamer':
                pass
            else:
                NSdict={'Room':zones.df.loc[zoneindex,'name'],'Capacity':flow,'Design pressure':supplyPressure,'Self-Regulating':'No'}
                jsondict['Natural supply'].append(NSdict)

                totalsup+=flow
    
    
        # ME for C supply
        if (system in ['CsupplyHall','CSLAAP']):
        
            if (zones.df.loc[zoneindex,'type'] in ['wet','dry']):
            
                function=zones.df.loc[zoneindex,'function']

                if (zones.df.loc[zoneindex,'name']=='Woonkamer' and 'OKeuken' in list(zones.df['name'])): # si cuisine ouverte, pas besoin d'extraction dans le sejour, tout sort a la cuisine
                    continue
                
                elif zones.df.loc[zoneindex,'name']=='OKeuken': #si cuisine ouvertre, le debit d'extraction est celui du sejour
                    
                    flow=computeflow('Woonkamer',boolbiggest,nbedrooms)

                else:
                    flow=computeflow(zones.df.loc[zoneindex,'function'],boolbiggest,nbedrooms)

                
                MEdict={'Room':zones.df.loc[zoneindex,'name'],'Nominal flow rate':flow}
                jsondict['Mechanical exhaust'].append(MEdict)
             
                totalexh+=flow

            
    # --------------------------------------------
    # Defining natural supply after all mechanical
    # --------------------------------------------
    
    nhals=len(zones.df[ (zones.df['type']=='hal') & (zones.df['outsideaccess']==True) ])
    
    if (system in ['CsupplyHall']):

        for zoneindex in zones.df[zones.df['type']=='hal'].index:
    
            if (zones.df.loc[zoneindex,'outsideaccess']==True):
    
                flow=totalexh/nhals
        
                NSdict={'Room':zones.df.loc[zoneindex,'name'],'Capacity':flow,'Design pressure':supplyPressure,'Self-Regulating':'No'}
                jsondict['Natural supply'].append(NSdict)



    return jsondict,totalsup,totalexh







def supplyAndExhaustBalancing(jsondict,system,zones,totalsup,totalexh,autobalancehal,autobalanceprop):
    
    #--------------
    # BALANCE
    #--------------

    imbalance=abs(totalsup-totalexh)

    if imbalance > 1.0:
        balance=False
    else:
        balance = True


    while (system in ['C','D','CRecyclage','DRecyclage'] and not balance):

        imbalance=totalsup-totalexh

        if (autobalancehal):
            #writetolog("Imbalance: ",imbalance," m3/h (supply:",totalsup,"m3/h, exhaust:",totalexh,"m3/h)")
            #writetolog("Automatic balancing")
            halzonesindex=zones.df[zones.df['type']=='hal'].index
            
            nhal=len(halzonesindex)

            factor=totalsup/totalexh


            if (nhal>0):
                for zoneid in halzonesindex:
                    
                    if factor > 1.0:

                        MEdict={'Room':zones.df.loc[zoneid,'name'],'Nominal flow rate':abs(imbalance)/nhal}
                        jsondict['Mechanical exhaust'].append(MEdict)
                        
                    else:
                        MSdict={'Room':zones.df.loc[zoneid,'name'],'Nominal flow rate':abs(imbalance)/nhal}
                        jsondict['Mechanical supply'].append(MSdict)
                        
                        
                totalexh+=abs(imbalance)

                break

            else:
                #writetolog("No hall to add additional extractions, increasing proportionally in wet spaces")
                autobalanceprop=True
            
        
        if (autobalanceprop):

            writetolog("Automatic balancing")            
            
            factor=totalsup/totalexh

            if factor > 1.0:
            
                for MEdict in jsondict['Mechanical exhaust']:
                    MEdict['Nominal flow rate']=MEdict['Nominal flow rate']*factor

            else:
                for MSdict in jsondict['Mechanical supply']:
                    MSdict['Nominal flow rate']=MSdict['Nominal flow rate']/factor
                

            break

        #writetolog("")
        #writetolog("WARNING: the system is unbalanced !")
        #writetolog("")
        #writetolog("Imbalance: ",totalsup-totalexh," m3/h (supply:",totalsup,"m3/h, exhaust:",totalexh,"m3/h)")
        #writetolog("")
        
        if (totalsup > totalexh) : # most common case
        
            
            #Adding extra exhaust in hal or dry spaces
            
            extraexh=input("Add extra exhaust in hal of dry spaces (y/n) ? ")
            
            if (extraexh in ['y','Y']):
            
                writetolog(zones.df[ (zones.df['type']=='hal') | (zones.df['type']=='dry')]['name'].to_string())
            
                ids=input("Select rooms in which to add an exhaust (room nr seperated with commas, e.g. 1,2,3 ) :  " )
            
                for roomid in [ int(x) for x in ids.split(',')]:
            
            
                    flow=float(input("Nominal flow rate for extract in room "+str(zones.df.loc[roomid,'name'])+' : '))

                    MEdict={'Room':zones.df.loc[roomid,'name'],'Nominal flow rate':flow}
                    jsondict['Mechanical exhaust'].append(MEdict)
                
                    totalexh+=flow
                
                    """writetolog("")
                    writetolog("Imbalance: ",totalsup-totalexh," m3/h (supply:",totalsup,"m3/h, exhaust:",totalexh,"m3/h)")
                    writetolog("")
                    """

            changeflowrate=input("Change flow rate of existing extractions ? (y/n) ")
        
            if (changeflowrate in ['y','Y']):

                #writetolog('{:3}'.format('id'), '{:12}'.format('Room'), '{:10}'.format('Flow rate') )
                
                for item in jsondict['Mechanical exhaust']:
                
                    roomid=zones.df[zones.df['name']==item['Room']].index[0]
                
                    #writetolog('{:3}'.format(str(roomid)), '{:12}'.format(item['Room']), '{:10}'.format(str(item['Nominal flow rate'])))

                ids=input("Choose rooms for wich to change the flow rate (roomid, separated by commas, e.g. 1,2,3) :  " )
                    
                for roomid in [ int(x) for x in ids.split()]:

                    flow=float(input("New flow rate for extract in room "+str(zones.df.loc[roomid,'name'])+' : '))

                    roomname=zones.df.loc[roomid,'name']
                    
                    for item in jsondict['Mechanical exhaust']:
                        if (item['Room']==roomname):
                            totalexh+= -item['Nominal flow rate']
                            item['Nominal flow rate']=flow
                            totalexh+= item['Nominal flow rate']
                            
                            """writetolog("")
                            writetolog("Imbalance: ",totalsup-totalexh," m3/h (supply:",totalsup,"m3/h, exhaust:",totalexh,"m3/h)")
                            writetolog("")"""
        #writetolog("Dry spaces")
        #writetolog(zones.df[zones.df['type']=='dry']['name'].to_string())
        
        
        #if (totalsup > totalexh) : # most common case
        
        

        if ( abs(totalsup - totalexh) > 1):
            balance=False
        else:
            """writetolog("")
            writetolog("Sufficient balance (<1 m3/h) is reached")
            writetolog("")"""
            balance=True

    
    return




def balanceNaturalTransfers(zones,flowelems,flowpaths,jsondict):    

    roombaldf = createRoomsBalanceTable(zones,jsondict)
    
    
    balanceDeadEndRooms(zones,flowpaths,flowelems,roombaldf)
 
    unbaldf=roombaldf[roombaldf['Balance'].abs() >1.0 ] #remaining unbalanced zones
        
    if (len(unbaldf)>0):
        allbalanced=False
    else:
        allbalanced=True
    
    nloops=0
    
    while (not allbalanced):
        
        nloops+=1

        allbalance,unbaldf = tryBalanceDryAndWetSpaces(zones,flowpaths,flowelems,roombaldf,unbaldf)

        #writetolog("unbal df after drywet")
        #writetolog(unbaldf)


        if ('WoonKeuken' in unbaldf.index):

            allbalanced,unbaldf = tryBalanceLivingAndOpenKitchen(zones,flowpaths,flowelems,roombaldf,unbaldf)
            #writetolog("unbal df after wk",unbaldf)
      
        if (len(unbaldf)==2):
                   
            allbalanced,unbaldf = tryBalanceTwoLastZones(zones,flowpaths,flowelems,roombaldf,unbaldf)
            #writetolog("unbal df after tow zones",unbaldf)
            
        else:
        
            
                    
            
            #writetolog("More than two zones are unbalanced, cannot easily find a solution")
            
            
            # one or more than two
            if (len(unbaldf)==1):
                writetolog("Only one unbalanced zone, impossible to perfectly balance natural transfers")
                break

     
            if nloops<3:
                #writetolog("Loop once more to see if it solves by itself")                
                continue

            
            else:
                #writetolog("Try forcing balance")
                # take the worst, and force it to transfer to an unbalanced neighbour. wz stands for Worst zone
                
                
                # we'll take them in the logical order: first solve the ones with only 1 trivial solution
                """remainingZones = list(unbaldf.index)

                writetolog(remainingZones)

                unbalancedNeighbours={}
                
                for zoneName in remainingZones:

                    zNeighbours=contam_functions.getNeighboursNamesWithNT(zoneName,zones.df,flowpaths.df,flowelems.df)
                    unbalancedZoneNeighbours=[ x for x in zNeighbours if x in unbaldf.index ] #on les garde seulement si pas balancees
                    
                
                    unbalancedNeighbours[zoneName] = unbalancedZoneNeighbours
                """
                wzName=unbaldf['Balance'].abs().idxmax()
                
                wzNeighbours=contam_functions.getNeighboursNamesWithNT(wzName,zones.df,flowpaths.df,flowelems.df)
                wzNeighbours=[ x for x in wzNeighbours if x in unbaldf.index ] #on les garde seulement si pas balancees



                #writetolog(wzName,wzNeighbours)

                try:
                    otherzone=wzNeighbours[0]
                except:
                    pass
                    # writetolog(wzName)
                    #writetolog(roombaldf.to_string())                        
                                  
                if (not pd.isna(roombaldf.loc[wzName,otherzone]) ):
                    roombaldf.loc[wzName,otherzone]+=-roombaldf.loc[wzName,'Balance']
                    roombaldf.loc[otherzone,wzName]+=roombaldf.loc[wzName,'Balance']

                else:
                    roombaldf.loc[wzName,otherzone]=-roombaldf.loc[wzName,'Balance']
                    roombaldf.loc[otherzone,wzName]=roombaldf.loc[wzName,'Balance']


                unbaldf = updateUnbalance(roombaldf,zones)

                
                if (len(unbaldf)==0):
                    allbalanced=True
                    break

    #when the table is full, apply the flows


    if ('WoonKeuken' in list(roombaldf.index)):
        roombaldf.drop(['WoonKeuken'],axis=0,inplace=True)
    
            
    for i in roombaldf.index:
        for c in roombaldf.drop(['Supply','Exhaust','Balance'],axis=1).columns:   #dropping balance, because if openkeukeun, balance per room is not 0
        
            if roombaldf.loc[i,c]>0:
            
                NTdict={'From room':i,
                        'To room':c,
                        'Capacity':roombaldf.loc[i,c],
                        'Design pressure':2
                        }   
                jsondict['Natural transfer'].append(NTdict)
      
            
    return jsondict



def createRoomsBalanceTable(zones,jsondict):
    
    cols=['Supply','Exhaust','Balance']+list(zones.df['name'])
    roombaldf=pd.DataFrame(index=zones.df['name'],columns=cols)

    roombaldf.loc[:,['Supply','Exhaust','Balance']]=0


    for network,devicelist in jsondict.items():
    
        if ('supply' in network or 'exhaust' in network):
            for device in devicelist:

                zonename=device['Room']
                
                if ('Capacity' in device.keys()):
                    flow=device['Capacity']
                if ('Nominal flow rate' in device.keys()):
                    flow=device['Nominal flow rate']
                
                if ('supply' in network):
                    roombaldf.loc[zonename,'Supply']+=flow
                if ('exhaust' in network):
                
                    #if ('Slaap' in zonename):
                        #one ignores mechanical exhaust in slaapkamers
                        #NO ! 
                    #    continue
                
                    roombaldf.loc[zonename,'Exhaust']+=flow*-1
                

    roombaldf['Balance']=roombaldf['Supply']+roombaldf['Exhaust']

    return roombaldf



def balanceDeadEndRooms(zones,flowpaths,flowelems,roombaldf):
    
    #for rooms with only one neighbouring zone, the natural transfer sizing is trivial
    # the only transfer possible is to the neighbouring room
    
    for zonename in zones.df['name']:

        
        neighbours=contam_functions.getNeighboursNamesWithNT(zonename,zones.df,flowpaths.df,flowelems.df)

        if (len(neighbours)==1):  # si une seule jonction, on peut équilibrer directement
            
            
            otherzonename=neighbours[0]

            roombaldf.loc[zonename,otherzonename]=-roombaldf.loc[zonename,'Balance']
            roombaldf.loc[otherzonename,zonename]=roombaldf.loc[zonename,'Balance']

            roombaldf['Balance']=roombaldf.drop(['Balance'],axis=1).sum(axis=1)


    # Considering Open Keuken & Woonkamer together --> duplicate them so that they have the same balance
    if ('OKeuken' in roombaldf.index):
        roombaldf.loc['WoonKeuken',:]=roombaldf.loc['Woonkamer',:]+roombaldf.loc['OKeuken',:]



def tryBalanceDryAndWetSpaces(zones,flowpaths,flowelems,roombaldf,unbaldf):
    
    
    allbalanced=False
    
    unbaldryzones=[ x for x in unbaldf.index if x in list(zones.df[zones.df['type']=='dry']['name'])]
    unbalwetzones=[ x for x in unbaldf.index if x in list(zones.df[zones.df['type']=='wet']['name'])]

    if ('OKeuken' in unbalwetzones):
        #special case to be handled apart
        unbalwetzones.remove('OKeuken')

        if ('Woonkamer' in unbaldryzones):
            unbaldryzones.remove('Woonkamer')
  
    #trying to balance dry and wet spaces with hals
    for zonename in unbaldryzones+unbalwetzones:
        
        zoneid=contam_functions.getzoneid(zonename,zones.df)
        zoneType = zones.df.loc[zoneid,'type']
        if zoneType=='dry':
            othertype='wet'
        elif zoneType=='wet':
            othertype='dry'
        
     
        neighbourzones=contam_functions.getNeighboursNamesWithNT(zonename,zones.df,flowpaths.df,flowelems.df) #byname
        
        neighbourhals=[ x for x in neighbourzones if x in list(zones.df[zones.df['type']=='hal']['name'])]
        
        if (len(neighbourhals)<1):
            
            otherTypeNeighbours=list(zones.df[ (zones.df['type']==othertype) & zones.df['name'].isin(neighbourzones)]['name'])

            if len(otherTypeNeighbours)==0:
                sameTypeNeighbours = list(zones.df[ (zones.df['type']==zoneType) & zones.df['name'].isin(neighbourzones)]['name'])
                otherzonename = sameTypeNeighbours[0]                    
            else:
            
                otherzonename=otherTypeNeighbours[0]

        else: #there is a neighbouring hall               
            otherzonename=neighbourhals[0]

        
        if (pd.isna(roombaldf.loc[zonename,otherzonename])):
            roombaldf.loc[zonename,otherzonename] = -roombaldf.loc[zonename,'Balance']
            roombaldf.loc[otherzonename,zonename] = roombaldf.loc[zonename,'Balance']
        else:
            roombaldf.loc[zonename,otherzonename] += -roombaldf.loc[zonename,'Balance']
            roombaldf.loc[otherzonename,zonename] += roombaldf.loc[zonename,'Balance']
        

        unbaldf = updateUnbalance(roombaldf,zones)


        if (len(unbaldf)==0):
            allbalanced=True
            break


    return allbalanced,unbaldf



def tryBalanceLivingAndOpenKitchen(zones,flowpaths,flowelems,roombaldf,unbaldf):

    
    allbalanced=False
    
    woonNeighbours=contam_functions.getNeighboursNamesWithNT('Woonkamer',zones.df,flowpaths.df,flowelems.df)
    keukenNeighbours=contam_functions.getNeighboursNamesWithNT('OKeuken',zones.df,flowpaths.df,flowelems.df)
    
    neighbourhals=[ x for x in woonNeighbours+keukenNeighbours if zones.df[zones.df['name']==x]['type'].iloc[0]=='hal']  #iloc --> otheriwse return series

    otherzonename=neighbourhals[0]

    roomtobalance='WoonKeuken'

    #par convention on va prendre le sejour is possible, sinon la cuisine
    if (otherzonename in woonNeighbours):
        zonename='Woonkamer'
    else:
        zonename='OKeuken'
                
    roombaldf.loc[zonename,otherzonename]=-roombaldf.loc[roomtobalance,'Balance']
    roombaldf.loc[otherzonename,zonename]=roombaldf.loc[roomtobalance,'Balance']

    unbaldf = updateUnbalance(roombaldf,zones)
        
    
    if (len(unbaldf)==0):
        allbalanced=True
       
    return allbalanced,unbaldf
        


def tryBalanceTwoLastZones(zones,flowpaths,flowelems,roombaldf,unbaldf):
    
    
    allbalanced=False
    #writetolog(unbaldf)
           
    zname1=unbaldf.index[0]
    zname2=unbaldf.index[1]
    
    commonpaths=contam_functions.getcommonNTpathsByName(zname1,zname2,zones.df,flowpaths.df,flowelems.df)

    if(len(commonpaths)==1):
     
        roombaldf.loc[zname1,zname2]=-roombaldf.loc[zname1,'Balance']
        roombaldf.loc[zname2,zname1]=roombaldf.loc[zname1,'Balance']

        unbaldf = updateUnbalance(roombaldf,zones)

    
        if (len(unbaldf)==0):
            allbalanced=True
            
    else:
        #writetolog("2 unbalanced zones remain, but no direct link between them")

        #we have to find if there is a common neighbour between the unbalanced spaces
        z1neighbours=contam_functions.getNeighboursNamesWithNT(zname1,zones.df,flowpaths.df,flowelems.df)
        z2neighbours=contam_functions.getNeighboursNamesWithNT(zname2,zones.df,flowpaths.df,flowelems.df)

        commonNeighbours= list(set(z1neighbours).intersection(set(z2neighbours))) #commonneighbour id
        
        if (len(commonNeighbours)==1):
        
            neighbourname=commonNeighbours[0]
            #writetolog("Neighbour zone",neighbourname)
        
            if (not pd.isna(roombaldf.loc[zname1,neighbourname]) ):
                roombaldf.loc[zname1,neighbourname]+=-roombaldf.loc[zname1,'Balance']
                roombaldf.loc[neighbourname,zname1]+=roombaldf.loc[zname1,'Balance']

            else:
                roombaldf.loc[zname1,neighbourname]=-roombaldf.loc[zname1,'Balance']
                roombaldf.loc[neighbourname,zname1]=roombaldf.loc[zname1,'Balance']

            if (not pd.isna(roombaldf.loc[neighbourname,zname2]) ):
                roombaldf.loc[neighbourname,zname2]+=-roombaldf.loc[zname1,'Balance']
                roombaldf.loc[zname2,neighbourname]+=roombaldf.loc[zname1,'Balance']

            else:
                roombaldf.loc[neighbourname,zname2]=-roombaldf.loc[zname1,'Balance']
                roombaldf.loc[zname2,neighbourname]=roombaldf.loc[zname1,'Balance']
                
  
            # writetolog(roombaldf)
            roombaldf['Balance']=roombaldf.drop(['Balance'],axis=1).sum(axis=1)
            #roombaldf.loc['WoonKeuken',:]=roombaldf.loc['Woonkamer',:]+roombaldf.loc['OKeuken',:]

        unbaldf = updateUnbalance(roombaldf,zones)
        #unbaldf.drop(['Woonkamer','OKeuken'],axis=0,inplace=True)
    
        if (len(unbaldf)==0):
            allbalanced=True
            

    return allbalanced,unbaldf



def updateUnbalance(roombaldf,zones):
   
    
    if('OKeuken' in list(zones.df['name'])):
        roombaldf.loc['WoonKeuken'] = roombaldf.loc[['Woonkamer','OKeuken']].sum()
        
    roombaldf['Balance'] = roombaldf.drop(['Balance'],axis=1).sum(axis=1)

    unbaldf=roombaldf[roombaldf['Balance'].abs() >1.0 ]
 
    if('WoonKeuken' not in list(unbaldf.index)):

        if ('OKeuken' in list(unbaldf.index)):
            unbaldf.drop(['Woonkamer','OKeuken'],axis=0,inplace=True)


    return unbaldf











