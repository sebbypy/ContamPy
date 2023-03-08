#import json
import sys
sys.path.append('../../')

import customExceptions
import contam_functions

import os
dirPath = os.path.dirname(os.path.realpath(__file__))
import sys
sys.path.append(os.path.join(dirPath,'../utilities'))

from utilityFunctions import shortenTooLongName


def setControls(contam_data,controlJSON):

    
    #with open('test.json', 'w') as outfile:
    #    json.dump(controlJSON, outfile)

    # ----------------------------------
    # Load CONTAM FILE and various parts
    # ----------------------------------

    zones=contam_data['zones']
    flowpaths=contam_data['flowpaths']
    controls=contam_data['controls']
    schedules=contam_data['dayschedules']
    weekschedules=contam_data['weekschedules']


    usedActuatorsNames=[]


    controlname_actuator_map={}
    nflows={}
    #map the actuator with the existing default control nodes (constant)
    # {C_MS_Woonakmaer:Actuatorname}
    # so that these control ids in the flow paths control can be replaced by 
    # the newly defined control ids

    #map also the actuator with the device name


    for ME in controlJSON['Mechanical exhaust']:

        if "Actuator" in ME.keys():
            usedActuatorsNames.append(ME["Actuator"])

            #getting existing controlID for this device

            controlname='C_ME_'+ME['Room']
            
            if (len(controlname)>15):
                controlname = shortenTooLongName(controlname,15)

            controlname_actuator_map[controlname]=ME['Actuator']
            nflows[controlname]=ME["Nominal flow rate"]
        


    for MS in controlJSON['Mechanical supply']:
    
        if "Actuator" in MS.keys():
            usedActuatorsNames.append(MS["Actuator"])

            controlname='C_MS_'+MS['Room']
            
            if (len(controlname)>15):
                controlname = shortenTooLongName(controlname,15)

            controlname_actuator_map[controlname]=MS['Actuator']
            nflows[controlname]=MS["Nominal flow rate"]


    if ('Windows' in controlJSON.keys()):
        for W in controlJSON['Windows']:
        
            if "Actuator" in W.keys():
                usedActuatorsNames.append(W["Actuator"])
                
                if W['Preferred orientation']=="":
                    
                    zoneid=zones.df[zones.df['name']==W['Room']].index[0]
                    fpid=flowpaths.df[ (flowpaths.df['pzm']==zoneid) & (flowpaths.df['pzn']==-1) ].index
                    controlname='C_NS_'+str(flowpaths.df.loc[fpid[1],'wazm'])+W['Room']
                else : 
                    controlname='C_NS_'+str(W["Preferred orientation"])+W['Room']
                    
                if (len(controlname)>15):
                    controlname = shortenTooLongName(controlname,15)

                controlname_actuator_map[controlname]=W['Actuator']


    if ('Natural supply' in controlJSON.keys()):
        for NS in controlJSON['Natural supply']:

            if "Actuator" in NS.keys():
                usedActuatorsNames.append(NS["Actuator"])


                if 'Preferred orientation' not in NS.keys():
                    zoneid=zones.df[zones.df['name']==NS['Room']].index[0]
                    fpid=flowpaths.df[ (flowpaths.df['pzm']==zoneid) & (flowpaths.df['pzn']==-1) ].index
                    controlname='C_NS_'+str(flowpaths.df.loc[fpid[1],'wazm'])+NS['Room']
                else:

                    controlname='C_NS_'+str(NS["Preferred orientation"])+NS['Room']
                
                if (len(controlname)>15):
                    controlname = shortenTooLongName(controlname,15)


                controlname_actuator_map[controlname]=NS['Actuator']
                nflows[controlname]=NS["Capacity"]



    if ('Ventilative cooling component' in controlJSON.keys()):
        for VC in controlJSON['Ventilative cooling component']:
        
            if "Actuator" in VC.keys():
                usedActuatorsNames.append(VC["Actuator"])
                zoneid=zones.df[zones.df['name']==VC['Room']].index[0]
                if VC['Preferred orientation']=="":
                    
                    
                    fpid=flowpaths.df[ (flowpaths.df['pzm']==zoneid)&(flowpaths.df['pzn']==-1)].index 
                    #print(fpid)
                    fpid=fpid[4]
                    
                    controlname='C_VC_'+str(flowpaths.df.loc[fpid,'wazm'])+VC['Room']
                    qname='Q_VC_'+str(flowpaths.df.loc[fpid,'wazm'])+VC['Room']
                else : 
                    
                    controlname='C_VC_'+str(VC["Preferred orientation"])+VC['Room']
                    qname='Q_VC_'+str(VC["Preferred orientation"])+VC['Room']
                    fpid=flowpaths.df[ (flowpaths.df['pzm']==zoneid)&(flowpaths.df['pzn']==-1)&(flowpaths.df['wazm'] == int(VC['Preferred orientation'])) ].index
                    fpid=fpid[3]
                    
                    
                if (len(controlname)>15):
                        controlname = shortenTooLongName(controlname,15)

                
                controlname_actuator_map[controlname]=VC['Actuator']
                controls.addconstant(controlname,1)
                flowpaths.df.loc[fpid,'pc']=controls.df.index[-1]
                controls.addflowsensor(fpid,qname)

               
    if ('Two ways door' in controlJSON.keys()):
        for D in controlJSON['Two ways door']:
        
            if "Actuator" in D.keys():
                usedActuatorsNames.append(D["Actuator"])
                roomid1=zones.df[zones.df['name']==D['From room']].index[0] # find ID of zone which has the same name
                roomid2=zones.df[zones.df['name']==D['To room']].index[0] # find ID of zone which has the same name
                commonflowpaths=contam_functions.getcommonpaths(flowpaths,roomid1,roomid2)  
                fpid=commonflowpaths.index[0]#premier choisi comme NT
                
                controlname='C_NT_'+str(fpid)
                
                if (len(controlname)>15):
                    controlname = shortenTooLongName(controlname,15)

                controlname_actuator_map[controlname]=D['Actuator']
                
                controls.addconstant('C_NT_'+str(fpid),1)
                flowpaths.df.loc[fpid,'pc']=controls.df.index[-1]
                controls.addflowsensor(fpid,'Q_NT_'+str(fpid))
                
                
       


    usedControlSignals=[]
    

    for A in usedActuatorsNames:

        Aobject=controlJSON["Actuators"][A]
    
        if (A not in controlJSON["Actuators"].keys()):
            print("Error, the actuator '",A,"' is used to control some devices but is not defined")

    
        if ("SignalName" in controlJSON["Actuators"][A].keys()):
    
            usedControlSignals.append(controlJSON["Actuators"][A]["SignalName"])



    sensordict={}  #sensor key:contamid
    
    if 'Signals' in controlJSON.keys():
    
        for Sname,Sdescription in controlJSON['Signals'].items():
        
        
            if (Sdescription["Type"]=="Single-Sensor"):
                
                checkZoneExist(zones,Sdescription['Room'])
                
                sensor_name=Sdescription['Specie']+'_'+Sdescription['Room']
                sensor_id=controls.df[controls.df['name']==sensor_name].index[0]
                sensordict[Sname]=sensor_id
            
            elif (Sdescription['Type']=="Max-Sensors"):
                
                sensors_ids=[]
                desc=''
                    
                for room in Sdescription["Rooms"]:
                    desc+=' '+room
                    sensor_name=Sdescription['Specie']+'_'+room
                    sensors_ids.append(controls.df[controls.df['name']==sensor_name].index[0])
            
                #def addMinMax(self,otype,name,inputs,description=''):
                controls.addMinMax('max','<none>',sensors_ids,"Max CO2 of rooms")
                sensor_id=controls.nctrl
                sensordict[Sname]=sensor_id
            
            elif (Sdescription['Type']=="Collector"):
                
                specie_sensors_ids=[]
                flow_sensors_ids=[]
                    
                for room in Sdescription["Rooms"]:
                    #species
                    sensor_name=Sdescription['Specie']+'_'+room
                    specie_sensors_ids.append(controls.df[controls.df['name']==sensor_name].index[0])
    
                    #extraction
                    sensor_name='Q_ME_'+room
                    
                    if (len(sensor_name)>15):
                        sensor_name = shortenTooLongName(sensor_name,15)
     
                    flow_sensors_ids.append(controls.df[controls.df['name']==sensor_name].index[0])
    
            
                #def addMinMax(self,otype,name,inputs,description=''):
                controls.addCollector(flow_sensors_ids,specie_sensors_ids,'Collector')
                sensor_id=controls.nctrl
                sensordict[Sname]=sensor_id
    
            elif (Sdescription['Type']=="Presence"):
            
                #print("Adding presence sensor")
            
                room=Sdescription['Room']
                occupancy_name='O_'+room
                occupancy_id=controls.df[controls.df['name']==occupancy_name].index[0]
                sensor_name="P_"+Sdescription["Room"]
                controls.addPresenceSensor(room,occupancy_id)
                
                sensordict[Sname]=controls.nctrl

            elif (Sdescription["Type"]=="Clock"):
                #print("Adding timer")
                controls.addClockControl(schedules,weekschedules,Sdescription["Schedule"],'nightClockSignal')

            
            elif (Sdescription["Type"]=="Single-TSensor"):
                  
                room=Sdescription['Room']
                if room != 'EXT':
                    zoneid=zones.df[zones.df['name']==room].index[0]
                else:
                    zoneid = -1
          
                controls.addtemperaturesensor(zones.df,zoneid,'T-sensor')
                sensordict[Sname]=controls.nctrl
                

            elif (Sdescription["Type"]=="Constant"):
                  
                value = Sdescription["Value"]
                controls.addconstant(str(value),value)
                sensordict[Sname]=controls.nctrl

    
                   
        #print(sensordict)
            
        actuatorscid={}
            
        #for A in usedActuatorsNames:
        for A in controlJSON["Actuators"].keys():
            
            
            Aobject=controlJSON["Actuators"][A]
            algoname=Aobject["ControlAlgorithmName"]
    
            AlgoObject=controlJSON["ControlAlgorithms"][algoname]
    
            if (AlgoObject["Type"]=="Linear"):
                controls.addLinearControl(sensordict[Aobject['SignalName']],AlgoObject["Qmin"],AlgoObject["Qmax"],AlgoObject["Vmin"],AlgoObject["Vmax"])
                
            elif (AlgoObject["Type"]=="Timer"):
                #print("Adding timer")
                controls.addTimerControl(schedules,sensordict[Aobject['SignalName']],AlgoObject["Qmin"],AlgoObject["Qmax"],AlgoObject["Duration"])
    
            elif (AlgoObject["Type"]=="Clock"):
                #print("Adding timer")
                controls.addClockControl(schedules,weekschedules,AlgoObject["Schedule"],algoname)
                    
                
            elif (AlgoObject["Type"]=="GreaterThanOtherSignal"):
             
                sensorid1 = sensordict[Aobject['SignalName']]
                sensorid2 = sensordict[Aobject['SignalName2']]
                                       
                controls.addGreaterThanOtherSignal(sensorid1,sensorid2)

            elif (AlgoObject["Type"]=="GreaterThanValue"):
             
                sensorid = sensordict[Aobject['SignalName']]
                value = AlgoObject['Value']                       
                
                controls.addGreaterThanValue(sensorid,value)



            elif (AlgoObject["Type"]=="IsBetween"):
                
                sensorid = sensordict[Aobject['SignalName']]
   
                lowerValueID = sensordict[Aobject['LowerValue']]
                upperValueID = sensordict[Aobject['UpperValue']]
                
                controls.addIsBetween(sensorid,lowerValueID,upperValueID)
                

            elif (AlgoObject['Type']=='Max'):

                signalsIdsList = []
                
                for actuatorName in Aobject["Actuators"]:
                    
                    try:
                        actuatorID = actuatorscid[actuatorName]
                        signalsIdsList.append(actuatorID)
                    except:
                        print("error, The actuator",actuatorName,"does not exist")
                        input('...')
                        exit()
                        
                controls.addMinMax('max','<none>',signalsIdsList,A)


            elif (AlgoObject['Type']=="WeightedSum"):
                
                signalsIdsList=[]
                for actuatorName in Aobject["Actuators"]:
                    
                    try:
                        actuatorID = actuatorscid[actuatorName]
                        
                        signalsIdsList.append(actuatorID)
                    except:
                        print("error, The actuator",actuatorName,"does not exist")
                        input('...')
                        exit()
                

                weights = Aobject["Weights"]
                
                controls.addWeightedSum(signalsIdsList,weights)
             
                    
                    

                
            else:
                raise ValueError(AlgoObject["Type"]+" does not exist yet")
                
            
            actuatorscid[A]=controls.nctrl

    
    #Creating balance control
       
    if ("Balances" in controlJSON.keys()):
    
        for balname,balrooms in controlJSON['Balances'].items():

            #input parameters: nominal flow and id of the local control
            balancedcontrolsids=controls.addBalanceControl(balrooms,nflows,controlname_actuator_map,actuatorscid)

    else:
        balancedcontrolsids={}


    if ("GlobalMinimumExtractControl" in controlJSON.keys()):
    
        globalActuatorName = controlJSON['GlobalMinimumExtractControl']['GlobalExtractActuator']    
    
        globalActuactorId = actuatorscid[globalActuatorName]

        
        extractRooms = controlJSON['GlobalMinimumExtractControl']['Rooms']
    
        globalextractcontrolids = controls.addGlobalExtractMinimumControlOnTopOfLocal(extractRooms,nflows,controlname_actuator_map,globalActuactorId ,actuatorscid)

    else:
        globalextractcontrolids = {}





   
    for controlname,actuatorname in controlname_actuator_map.items():
    #loop the old ids (default constant) and replace it by the new ones
        
        if (not controlname in list(controls.df['name']) ):
            #means the control does not exist, which also means the device does not exist!
            print("Warning ! Control ",controlname,"does not exist XX!")
            continue
        
        oldCid=controls.df[controls.df['name']==controlname].index[0]

        if (controlname in balancedcontrolsids):
            newCid=balancedcontrolsids[controlname]

        elif controlname in globalextractcontrolids:
            newCid = globalextractcontrolids[controlname]

        else:
            newCid=actuatorscid[actuatorname]

  
        flowpaths.df.loc[flowpaths.df['pc'].astype(int)==oldCid,'pc']=newCid
        
        #adding report of controls in log file!
        # Header is the heaeder of the log file
        controls.addreport(newCid,'R'+controlname,reporttype='',description='',header=controlname)
    





def doZoneExist(zones,zoneName):

    return zoneName in zones.df['name'].values
    

def checkZoneExist(zones,zoneName):
    
    if not doZoneExist(zones,zoneName):
        raise customExceptions.ContamPyException("Zone "+zoneName+" does not exist in the current model") 
        
        
        
        
