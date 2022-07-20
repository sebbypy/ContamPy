import sys
sys.path.append('/home/spec/Documents/Projects/RESEARCH/COMISVENT/2.Work/Python')

import copy

def getListOfRoomsFromJson(systemJson):
    
    rooms = []
    
    for deviceType,deviceList in systemJson.items():
        
        if 'supply' in deviceType or 'exhaust' in deviceType:
            
            for device in deviceList:

                rooms.append(device['Room'])

        if 'transfer' in deviceType:
            
            for device in deviceList:
                
                rooms.append(device['From room'])
                rooms.append(device['To room'])
    
    
    return list(set(rooms))
    

def compute(**kwargs):
    
    
    #--------------------------------------------
    # Defining types (wet/dry/hal) and functions
    #--------------------------------------------
    wet=['Wasplaats','Badkamer','WC','Keuken','OKeuken']  # existing functions in dry spaces
    dry=['Slaapkamer','Woonkamer','Bureau','Speelkamer']  # existing function in wet spaces
    hal=['hal','Hal','Garage','Berging','Dressing'] #existing functions for hal



    systemJson = kwargs['systemJson']
    strategy = kwargs['strategy']
    #systemJson = args[0]
    #strategy = args[1]

    
    controlJson = copy.deepcopy(systemJson)


    balance=False
    
    #if (len(args)>2):
    #    if (args[2]=="balanced"):
    #        balance=True
    if 'balance' in kwargs.keys():
        balance=kwargs['balance']
    
    if 'minFlow' in kwargs.keys():
        minFlow = kwargs['minFlow']
    else:
        minFlow = 0.1
    
    if 'maxFlow' in kwargs.keys():
        maxFlow = kwargs['maxFlow']
    else:
        maxFlow = 1.0

    if 'nightFlow' in kwargs.keys():
        nightFlow = kwargs['nightFlow']
    else:
        nightFlow = maxFlow

    if ('flowFraction' in kwargs.keys()):
        flowFraction = kwargs['flowFraction']
    else:
        flowFraction = None


    if (strategy=='singleClock'):
        schedule = kwargs['schedule']


    # 1. Reference algorithms

    refalgos={
        "CO2-Linear":
            {"Type":"Linear","Qmin":minFlow,"Qmax":1.0,"Vmin":500,"Vmax":1000},
        "H2O-Linear":
            {"Type":"Linear","Qmin":minFlow,"Qmax":1.0,"Vmin":0.3,"Vmax":0.7},
        "Timer30min":
            {"Type":"Timer","Qmin":minFlow,"Qmax": 1,"Duration": "30min"},
        "NightClock":{
                    "Type":"Clock",
                    "Schedule":{
                        "00:00:00":nightFlow,
                        "07:00:00":minFlow,
                        "23:00:00":nightFlow,
                        "24:00:00":nightFlow
                        }
                    },
        "DayClock":{
                    "Type":"Clock",
                    "Schedule":{
                        "00:00:00":minFlow,
                        "08:00:00":1.0,
                        "22:00:00":minFlow,
                        "24:00:00":minFlow
                        }
                    },
        "ConstantClock":{
                    "Type":"Clock",
                    "Schedule":{
                        "00:00:00":flowFraction,
                        "24:00:00":flowFraction
                        }
                    },
        "Max":{
                    "Type":"Max",
                    },                    
        }
    
    controlJson["ControlAlgorithms"]=refalgos
    
    # 2. Detecting all rooms (with mecanical or natural controllable device)

    supplyrooms=[ x["Room"] for x in controlJson["Mechanical supply"] ]
    exhaustrooms=[ x["Room"] for x in controlJson["Mechanical exhaust"] ]

    if ('Natural supply' in controlJson.keys()):
        naturalsupplyrooms=[ x["Room"] for x in controlJson["Natural supply"] ]
    else:
        naturalsupplyrooms = []

    if ('Windows' in controlJson.keys()):
        windowrooms=[ x["Room"] for x in controlJson["Windows"] ]
    else:
        controlJson["Windows"]=[]
        windowrooms=[]
    #print(supplyrooms,exhaustrooms)
    allrooms=supplyrooms+exhaustrooms+windowrooms+naturalsupplyrooms

    # 3. Adding signals

    controlJson["Signals"]={}
    controlJson["Actuators"]={}
   
      
    #if (strategy=='fulllocal' or strategy=='fulllocalRTOs' or strategy=='fulllocalRTOsBal'):
    
    if strategy == 'constant' and flowFraction != None:
        
        actuatordict={'SignalName':'','ControlAlgorithmName':'ConstantClock'}
        controlJson["Actuators"]["ConstantClockActuator"]=actuatordict
        for x in controlJson["Mechanical supply"]+controlJson["Mechanical exhaust"]:
            x["Actuator"]="ConstantClockActuator"
    
    
    if strategy in ['fulllocal','fulllocalRTOs','fulllocalRTOsBal']:
    
        wet.remove('OKeuken')
        dry.append('OKeuken')
    
        #dry - CO2 sensors
        for r in allrooms: #room name

            #uitzonderingen eerst
            for d in dry+hal: #list of all existing dry
                if (d in r):
                
                    signaldict={"Type":"Single-Sensor","Specie":"CO2","Room":r}
                    controlJson["Signals"]["CO2-"+r]=signaldict
            
                    actuatordict={"SignalName":"CO2-"+r,"ControlAlgorithmName":"CO2-Linear"}
                    
                    controlJson["Actuators"]["CO2-"+r+"-linear"]=actuatordict
                    
                    
                    for x in controlJson["Mechanical supply"]+controlJson["Mechanical exhaust"]+controlJson["Windows"]:
                        if (x["Room"]==r):
                            x["Actuator"]="CO2-"+r+"-linear"
                    
                    
                    if (strategy=='fulllocalRTOs' or strategy=='fulllocalRTOsBal'):
                        for x in controlJson["Natural supply"]:
                            if (x["Room"]==r):
                                x["Actuator"]="CO2-"+r+"-linear"
                                
                    
                    
                    
                    break
            
            for w in wet: #list of all existing dry
            
                if (r=='OKeuken'):
                    continue
            
                if (w in r):
                
                    if (w=='WC'):
                        signaldict={'Type':'Presence','Room':r}
                        
                        controlJson["Signals"]["Pres-"+r]=signaldict

                        
                        actuatordict={"SignalName":"Pres-"+r,"ControlAlgorithmName":"Timer30min"}
                        controlJson["Actuators"][r+'-Timer']=actuatordict
                        for x in controlJson["Mechanical supply"]+controlJson["Mechanical exhaust"]+controlJson["Windows"]:
                            if (x["Room"]==r):
                                x["Actuator"]=r+"-Timer"

                        continue
                
                
                
                    signaldict={"Type":"Single-Sensor","Specie":"H2O","Room":r}
                    controlJson["Signals"]["H2O-"+r]=signaldict

                    actuatordict={"SignalName":"H2O-"+r,"ControlAlgorithmName":"H2O-Linear"}

                    controlJson["Actuators"]["H2O-"+r+"-linear"]=actuatordict

                    for x in controlJson["Mechanical supply"]+controlJson["Mechanical exhaust"]+controlJson["Windows"]:
                        if (x["Room"]==r):
                            x["Actuator"]="H2O-"+r+"-linear"

                        
                    break

                    
                    

            

    if (strategy == 'CO2Central'):
        print("applying CO2 central")
        r='Woonkamer'
        
        signaldict={"Type":"Single-Sensor","Specie":"CO2","Room":r}
        controlJson["Signals"]["CO2-"+r]=signaldict
        actuatordict={"SignalName":"CO2-"+r,"ControlAlgorithmName":"CO2-Linear"}
        controlJson["Actuators"]["CO2-"+r+"-linear"]=actuatordict
     

        for x in controlJson["Mechanical supply"]+controlJson["Mechanical exhaust"]+controlJson["Windows"]:
            x["Actuator"]="CO2-"+r+"-linear"
            

    if (strategy == 'CO2CentralHall'):
        print("applying CO2 central hall")


    

        r='Hal'
        
        CO2LinearHal={"Type":"Linear","Qmin":minFlow,"Qmax":1.0,"Vmin":450,"Vmax":650}
        
        
        controlJson["ControlAlgorithms"]['CO2-Linear-Hal']= CO2LinearHal
        
        signaldict={"Type":"Single-Sensor","Specie":"CO2","Room":r}
        controlJson["Signals"]["CO2-"+r]=signaldict
        actuatordict={"SignalName":"CO2-"+r,"ControlAlgorithmName":"CO2-Linear-Hal"}
        controlJson["Actuators"]["CO2-"+r+"-linear"]=actuatordict
     

        for x in controlJson["Mechanical supply"]+controlJson["Mechanical exhaust"]:
            x["Actuator"]="CO2-"+r+"-linear"
            


    if (strategy == 'NightClockCO2Central'):
        
        print("applying CO2 central + a night clock")
        r='Woonkamer'

        #Adding CO2 signal and linear actuator        
        signaldict={"Type":"Single-Sensor","Specie":"CO2","Room":r}
        controlJson["Signals"]["CO2-"+r]=signaldict

        actuatordict={"SignalName":"CO2-"+r,"ControlAlgorithmName":"CO2-Linear"}
        controlJson["Actuators"]["CO2-"+r+"-linear"]=actuatordict


        #Adding clock actuator
        actuatordict={'SignalName':'','ControlAlgorithmName':'NightClock'}
        controlJson["Actuators"]["NightClockActuator"]=actuatordict


        #Computing max actuator
     
        actuatordict={"ControlAlgorithmName":"Max","Actuators":[]}
        actuatordict["Actuators"].append("CO2-"+r+"-linear")
        actuatordict["Actuators"].append("NightClockActuator")

        controlJson["Actuators"]["MaxCO2AndNightclock"]=actuatordict


        for x in controlJson["Mechanical supply"]+controlJson["Mechanical exhaust"]+controlJson["Windows"]:
            x["Actuator"]="MaxCO2AndNightclock"
    

    if (strategy == 'NightClockCO2Local'):
        
        print("applying CO2 local + a night clock")

        r='Woonkamer'

        #Adding CO2 signal and linear actuator        
        signaldict={"Type":"Single-Sensor","Specie":"CO2","Room":r}
        controlJson["Signals"]["CO2-"+r]=signaldict

        actuatordict={"SignalName":"CO2-"+r,"ControlAlgorithmName":"CO2-Linear"}
        controlJson["Actuators"]["CO2-"+r+"-linear"]=actuatordict


        #Adding clock actuator
        actuatordict={'SignalName':'','ControlAlgorithmName':'NightClock'}
        controlJson["Actuators"]["NightClockActuator"]=actuatordict


        for x in controlJson["Mechanical supply"]+controlJson["Mechanical exhaust"]+controlJson["Windows"]:

            if ('Slaap' in x['Room']):
                x["Actuator"]="NightClockActuator"
            
            if x['Room'] in ['OKeuken','Woonkamer','Keuken']:
            
                x["Actuator"]="CO2-"+'Woonkamer'+"-linear"


            if (x['Room']=='WC'):
                
                r='WC'
                signaldict={'Type':'Presence','Room':r}
                controlJson["Signals"]["Pres-"+r]=signaldict
                
                actuatordict={"SignalName":"Pres-"+r,"ControlAlgorithmName":"Timer30min"}
                controlJson["Actuators"][r+'-Timer']=actuatordict

                x["Actuator"]=r+"-Timer"
        
        
            if x['Room'] in ['Wasplaats','Badkamer','Douche']:        

                r=x['Room']
                
                
                signaldict={"Type":"Single-Sensor","Specie":"H2O","Room":r}
                controlJson["Signals"]["H2O-"+r]=signaldict
    
                actuatordict={"SignalName":"H2O-"+r,"ControlAlgorithmName":"H2O-Linear"}
    
                controlJson["Actuators"]["H2O-"+r+"-linear"]=actuatordict
    
                x["Actuator"]="H2O-"+r+"-linear"


    if strategy=='allMotRTOAndGlobalExtract':
        
        
        dryActuators = []        
        
        
        for x in controlJson["Natural supply"]:
            r = x["Room"]

            signaldict={"Type":"Single-Sensor","Specie":"CO2","Room":r}
            controlJson["Signals"]["CO2-"+r]=signaldict
            
            actuatordict={"SignalName":"CO2-"+r,"ControlAlgorithmName":"CO2-Linear"}                    
            controlJson["Actuators"]["CO2-"+r+"-linear"]=actuatordict
 
            x["Actuator"]="CO2-"+r+"-linear"
         
                
            dryActuators.append(x['Actuator'])
            
        for x in controlJson["Mechanical exhaust"]:

            
            r=x['Room']

            if (r=='WC'):
                signaldict={'Type':'Presence','Room':r}
                controlJson["Signals"]["Pres-"+r]=signaldict
                       
                actuatordict={"SignalName":"Pres-"+r,"ControlAlgorithmName":"Timer30min"}
                controlJson["Actuators"][r+'-Timer']=actuatordict

                localActuatorName = r+'-Timer'
 
            else:           
                signaldict={"Type":"Single-Sensor","Specie":"H2O","Room":r}
                controlJson["Signals"]["H2O-"+r]=signaldict

                actuatordict={"SignalName":"H2O-"+r,"ControlAlgorithmName":"H2O-Linear"}
                controlJson["Actuators"]["H2O-"+r+"-linear"]=actuatordict

                localActuatorName = "H2O-"+r+"-linear"

            
            newactuatordict={"ControlAlgorithmName":"Max","Actuators":[]}
            newactuatordict["Actuators"].append(localActuatorName)
            newactuatordict["Actuators"] += dryActuators
            controlJson["Actuators"]["Global-"+r]=newactuatordict


            x["Actuator"]="Global-"+r




    if strategy=='oneMotRTOAndGlobalExtract':
        
        
        dryActuators = []        
        
        maxSlaapFlow = 0
        biggestBedRoom = None


        for x in controlJson["Natural supply"]:
            r = x["Room"]

            if 'Slaap' in r:
                
                flow = x['Capacity']
                if (flow > maxSlaapFlow):
                    maxSlaapFlow = flow
                    biggestBedRoom = r

        signaldict={"Type":"Single-Sensor","Specie":"CO2","Room":biggestBedRoom}
        controlJson["Signals"]["CO2-"+biggestBedRoom]=signaldict
                
        actuatordict={"SignalName":"CO2-"+biggestBedRoom,"ControlAlgorithmName":"CO2-Linear"}                    
        controlJson["Actuators"]["CO2-"+biggestBedRoom+"-linear"]=actuatordict
        
        dryActuators.append("CO2-"+biggestBedRoom+"-linear")
        
        for x in controlJson["Natural supply"]:
            r = x["Room"]

            if r=='Woonkamer':
        
                signaldict={"Type":"Single-Sensor","Specie":"CO2","Room":r}
                controlJson["Signals"]["CO2-"+r]=signaldict
                
                actuatordict={"SignalName":"CO2-"+r,"ControlAlgorithmName":"CO2-Linear"}                    
                controlJson["Actuators"]["CO2-"+r+"-linear"]=actuatordict
         
                x["Actuator"]="CO2-"+r+"-linear"
             
                    
                dryActuators.append(x['Actuator'])


        
                    
            

            
        for x in controlJson["Mechanical exhaust"]:
    
            
            r=x['Room']
    
            if (r=='WC'):
                signaldict={'Type':'Presence','Room':r}
                controlJson["Signals"]["Pres-"+r]=signaldict
                       
                actuatordict={"SignalName":"Pres-"+r,"ControlAlgorithmName":"Timer30min"}
                controlJson["Actuators"][r+'-Timer']=actuatordict
    
                localActuatorName = r+'-Timer'
     
            else:           
                signaldict={"Type":"Single-Sensor","Specie":"H2O","Room":r}
                controlJson["Signals"]["H2O-"+r]=signaldict
    
                actuatordict={"SignalName":"H2O-"+r,"ControlAlgorithmName":"H2O-Linear"}
                controlJson["Actuators"]["H2O-"+r+"-linear"]=actuatordict
    
                localActuatorName = "H2O-"+r+"-linear"
    
            
            newactuatordict={"ControlAlgorithmName":"Max","Actuators":[]}
            newactuatordict["Actuators"].append(localActuatorName)
            newactuatordict["Actuators"] += dryActuators
            controlJson["Actuators"]["Global-"+r]=newactuatordict
    
    
            x["Actuator"]="Global-"+r


    if strategy=='Zonal1RTO':
        
        #for C Cascade or CPREVENT (motorized RTO)
        
        rooms = getListOfRoomsFromJson(systemJson)
        
        if 'Nachthal' in rooms:
            refhal = 'Nachthal'
        elif 'NachtHal' in rooms:
            refhal = 'NachtHal'
        elif 'Hal' in rooms:
            refhal = 'Hal'
        elif 'Inkomhal' in rooms:
            refhal = 'Inkomhal'
        else:
            print("ERROR, CANNOT FIND HAL")
            raise
                
        
        dryActuators = []        
        
        maxSlaapFlow = 0
        biggestBedRoom = None


        nSlaaps = 0

        for x in controlJson["Natural supply"]:
            r = x["Room"]

            if 'Slaap' in r:
                nSlaaps += 1

        signaldict={"Type":"Single-Sensor","Specie":"CO2","Room":refhal}
        controlJson["Signals"]["CO2-"+refhal]=signaldict
                
        
        halAlgo = {"Type":"Linear","Qmin":0.3,"Qmax":1.0,"Vmin":450,"Vmax":400+600/nSlaaps}
        controlJson["ControlAlgorithms"]["CO2-Linear-Hall"] = halAlgo
        
        
        actuatordict={"SignalName":"CO2-"+refhal,"ControlAlgorithmName":"CO2-Linear-Hall"}                    
        controlJson["Actuators"]["CO2-"+refhal+"-linear"]=actuatordict
        
        dryActuators.append("CO2-"+refhal+"-linear")
        
        for x in controlJson["Natural supply"]:
            r = x["Room"]

            if r=='Woonkamer':
        
                signaldict={"Type":"Single-Sensor","Specie":"CO2","Room":r}
                controlJson["Signals"]["CO2-"+r]=signaldict
                
                actuatordict={"SignalName":"CO2-"+r,"ControlAlgorithmName":"CO2-Linear"}                    
                controlJson["Actuators"]["CO2-"+r+"-linear"]=actuatordict
         
                x["Actuator"]="CO2-"+r+"-linear"
             
                    
                dryActuators.append(x['Actuator'])

            
        for x in controlJson["Mechanical exhaust"]:
    
            
            r=x['Room']
    
            if (r=='WC'):
                signaldict={'Type':'Presence','Room':r}
                controlJson["Signals"]["Pres-"+r]=signaldict
                       
                actuatordict={"SignalName":"Pres-"+r,"ControlAlgorithmName":"Timer30min"}
                controlJson["Actuators"][r+'-Timer']=actuatordict
    
                localActuatorName = r+'-Timer'
     
            elif ('Woon' in r or 'OKeuken' in r):
                signaldict={"Type":"Single-Sensor","Specie":"CO2","Room":r}
                controlJson["Signals"]["CO2-"+r]=signaldict
    
                actuatordict={"SignalName":"CO2-"+r,"ControlAlgorithmName":"CO2-Linear"}
                controlJson["Actuators"]["CO2-"+r+"-linear"]=actuatordict
    
                localActuatorName = "CO2-"+r+"-linear"
    
     
            else:           
                signaldict={"Type":"Single-Sensor","Specie":"H2O","Room":r}
                controlJson["Signals"]["H2O-"+r]=signaldict
    
                actuatordict={"SignalName":"H2O-"+r,"ControlAlgorithmName":"H2O-Linear"}
                controlJson["Actuators"]["H2O-"+r+"-linear"]=actuatordict
    
                localActuatorName = "H2O-"+r+"-linear"
    
            
            newactuatordict={"ControlAlgorithmName":"Max","Actuators":[]}
            newactuatordict["Actuators"].append(localActuatorName)
            newactuatordict["Actuators"] += dryActuators
            controlJson["Actuators"]["Global-"+r]=newactuatordict
    
    
            x["Actuator"]="Global-"+r


    if strategy=='noMotRTOAndGlobalExtract':
        
        
        
        dryActuators = []        
        
        maxSlaapFlow = 0
        biggestBedRoom = None


        for x in controlJson["Natural supply"]:
            r = x["Room"]

            if 'Slaap' in r:
                
                flow = x['Capacity']
                if (flow > maxSlaapFlow):
                    maxSlaapFlow = flow
                    biggestBedRoom = r

        signaldict={"Type":"Single-Sensor","Specie":"CO2","Room":biggestBedRoom}
        controlJson["Signals"]["CO2-"+biggestBedRoom]=signaldict
                
        actuatordict={"SignalName":"CO2-"+biggestBedRoom,"ControlAlgorithmName":"CO2-Linear"}                    
        controlJson["Actuators"]["CO2-"+biggestBedRoom+"-linear"]=actuatordict
        
        dryActuators.append("CO2-"+biggestBedRoom+"-linear")
        
        for x in controlJson["Natural supply"]:
            r = x["Room"]

            if r=='Woonkamer':
        
                signaldict={"Type":"Single-Sensor","Specie":"CO2","Room":r}
                controlJson["Signals"]["CO2-"+r]=signaldict
                
                actuatordict={"SignalName":"CO2-"+r,"ControlAlgorithmName":"CO2-Linear"}                    
                controlJson["Actuators"]["CO2-"+r+"-linear"]=actuatordict
                    
                dryActuators.append("CO2-"+r+"-linear")

            

            
        for x in controlJson["Mechanical exhaust"]:
    
            
            r=x['Room']
    
            if (r=='WC'):
                signaldict={'Type':'Presence','Room':r}
                controlJson["Signals"]["Pres-"+r]=signaldict
                       
                actuatordict={"SignalName":"Pres-"+r,"ControlAlgorithmName":"Timer30min"}
                controlJson["Actuators"][r+'-Timer']=actuatordict
    
                localActuatorName = r+'-Timer'
     
            else:           
                signaldict={"Type":"Single-Sensor","Specie":"H2O","Room":r}
                controlJson["Signals"]["H2O-"+r]=signaldict
    
                actuatordict={"SignalName":"H2O-"+r,"ControlAlgorithmName":"H2O-Linear"}
                controlJson["Actuators"]["H2O-"+r+"-linear"]=actuatordict
    
                localActuatorName = "H2O-"+r+"-linear"
    
            
            newactuatordict={"ControlAlgorithmName":"Max","Actuators":[]}
            newactuatordict["Actuators"].append(localActuatorName)
            newactuatordict["Actuators"] += dryActuators
            controlJson["Actuators"]["Global-"+r]=newactuatordict
    
    
            x["Actuator"]="Global-"+r


                    
                    
    if (balance and strategy!='constant'):
        controlJson["Balances"]={}
        controlJson["Balances"]["Global"]=allrooms
                    

    
    #json.dump(controlJson,open(controljson,'w'),indent=4)
    return controlJson

