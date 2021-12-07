

def setControls(contam_data,controlJSON):

    # ----------------------------------
    # Load CONTAM FILE and various parts
    # ----------------------------------

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
                controlname=controlname.replace('kamer','')

            controlname_actuator_map[controlname]=ME['Actuator']
            nflows[controlname]=ME["Nominal flow rate"]
        


    for MS in controlJSON['Mechanical supply']:
    
        if "Actuator" in MS.keys():
            usedActuatorsNames.append(MS["Actuator"])

            controlname='C_MS_'+MS['Room']
            
            if (len(controlname)>15):
                controlname=controlname.replace('kamer','')

            controlname_actuator_map[controlname]=MS['Actuator']
            nflows[controlname]=MS["Nominal flow rate"]


    if ('Windows' in controlJSON.keys()):
        for W in controlJSON['Windows']:
        
            if "Actuator" in W.keys():
                usedActuatorsNames.append(W["Actuator"])

                controlname='C_NS_'+W['Room']
                
                if (len(controlname)>15):
                    controlname=controlname.replace('kamer','')

                controlname_actuator_map[controlname]=W['Actuator']


    if ('Natural supply' in controlJSON.keys()):
        for NS in controlJSON['Natural supply']:
        
            if "Actuator" in NS.keys():
                usedActuatorsNames.append(NS["Actuator"])

                controlname='C_NS_'+NS['Room']
                
                if (len(controlname)>15):
                    controlname=controlname.replace('kamer','')

                controlname_actuator_map[controlname]=NS['Actuator']
                nflows[controlname]=NS["Capacity"]



    usedControlSignals=[]
    

    for A in usedActuatorsNames:

        Aobject=controlJSON["Actuators"][A]
    
        if (A not in controlJSON["Actuators"].keys()):
            print("Error, the actuator '",A,"' is used to control some devices but is not defined")
    
        usedControlSignals.append(controlJSON["Actuators"][A]["SignalName"])



    sensordict={}  #sensor key:contamid
    
    if 'Signals' in controlJSON.keys():
    
        for Sname,Sdescription in controlJSON['Signals'].items():
        
        
            if (Sdescription["Type"]=="Single-Sensor"):
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
                        sensor_name=sensor_name.replace('kamer','')
     
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
    
                   
        #print(sensordict)
            
        actuatorscid={}
            
        for A in usedActuatorsNames:
            
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
                    
                
            else:
                print(AlgoObject["Type"]+" does not exist yet")
                exit()
            
            actuatorscid[A]=controls.nctrl
            

    
    #Creating balance control
       
    if ("Balances" in controlJSON.keys()):
    
        for balname,balrooms in controlJSON['Balances'].items():

            #input parameters: nominal flow and id of the local control
            balancedcontrolsids=controls.addBalanceControl(balrooms,nflows,controlname_actuator_map,actuatorscid)

    else:
        balancedcontrolsids={}

   
    for controlname,actuatorname in controlname_actuator_map.items():
    #loop the old ids (default constant) and replace it by the new ones
        
        if (not controlname in list(controls.df['name']) ):
            #means the control does not exist, which also means the device does not exist!
            print("Warning ! Control ",controlname,"does not exist!")
            continue
        
        oldCid=controls.df[controls.df['name']==controlname].index[0]

        if (controlname in balancedcontrolsids):
            newCid=balancedcontrolsids[controlname]

        else:
            newCid=actuatorscid[actuatorname]

  
        flowpaths.df.loc[flowpaths.df['pc'].astype(int)==oldCid,'pc']=newCid
        
    
