import sys
sys.path.append('/home/spec/Documents/Projects/RESEARCH/COMISVENT/2.Work/Python')

import copy

    
def compute(args):
    
    
    #--------------------------------------------
    # Defining types (wet/dry/hal) and functions
    #--------------------------------------------
    wet=['Wasplaats','Badkamer','WC','Keuken','OKeuken']  # existing functions in dry spaces
    dry=['Slaapkamer','Woonkamer','Bureau','Speelkamer']  # existing function in wet spaces
    hal=['hal','Hal','Garage','Berging','Dressing'] #existing functions for hal


    systemJson = args[0]
    strategy = args[1]
    
    controlJson = copy.deepcopy(systemJson)


    balance=False
    
    if (len(args)>2):
        if (args[2]=="balanced"):
            balance=True
    

    # 1. Reference algorithms

    refalgos={
        "CO2-Linear-10pc":
            {"Type":"Linear","Qmin":0.1,"Qmax":1.0,"Vmin":500,"Vmax":1000},
        "H2O-Linear-10pc":
            {"Type":"Linear","Qmin":0.1,"Qmax":1.0,"Vmin":0.3,"Vmax":0.7},
        "CO2-Linear-30pc":
            {"Type":"Linear","Qmin":0.3,"Qmax":1.0,"Vmin":500,"Vmax":1000},
        "H2O-Linear-30pc":
            {"Type":"Linear","Qmin":0.3,"Qmax":1.0,"Vmin":0.3,"Vmax":0.7},
        "Timer30min":
            {"Type":"Timer","Qmin": 0.1,"Qmax": 1,"Duration": "30min"},
        "NightClock":{
                    "Type":"Clock",
                    "Schedule":{
                        "00:00:00":1.0,
                        "08:00:00":0.1,
                        "20:00:00":1.0,
                        "24:00:00":1.0
                        }
                    },
        "DayClock":{
                    "Type":"Clock",
                    "Schedule":{
                        "00:00:00":0.1,
                        "08:00:00":1.0,
                        "22:00:00":0.1,
                        "24:00:00":0.1
                        }
                    }
        }
    
    controlJson["ControlAlgorithms"]=refalgos
    
    # 2. Detecting all rooms (with mecanical or natural controllable device)

    supplyrooms=[ x["Room"] for x in controlJson["Mechanical supply"] ]
    exhaustrooms=[ x["Room"] for x in controlJson["Mechanical exhaust"] ]

    if ('Windows' in controlJson.keys()):
        windowrooms=[ x["Room"] for x in controlJson["Windows"] ]
    else:
        controlJson["Windows"]=[]
        windowrooms=[]
    #print(supplyrooms,exhaustrooms)
    allrooms=supplyrooms+exhaustrooms+windowrooms

    # 3. Adding signals

    controlJson["Signals"]={}
    controlJson["Actuators"]={}
   
      
    if (strategy=='fulllocal'):
    
        wet.remove('OKeuken')
        dry.append('OKeuken')
    
        #dry - CO2 sensors
        for r in allrooms: #room name

            #uitzonderingen eerst
            
        
            for d in dry: #list of all existing dry
                if (d in r):
                
                    signaldict={"Type":"Single-Sensor","Specie":"CO2","Room":r}
                    controlJson["Signals"]["CO2-"+r]=signaldict
            
                    actuatordict={"SignalName":"CO2-"+r,"ControlAlgorithmName":"CO2-Linear-10pc"}
                    
                    controlJson["Actuators"]["CO2-"+r+"-linear"]=actuatordict
                    
                    
                    for x in controlJson["Mechanical supply"]+controlJson["Mechanical exhaust"]+controlJson["Windows"]:
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

                    actuatordict={"SignalName":"H2O-"+r,"ControlAlgorithmName":"H2O-Linear-10pc"}

                    controlJson["Actuators"]["H2O-"+r+"-linear"]=actuatordict

                    for x in controlJson["Mechanical supply"]+controlJson["Mechanical exhaust"]+controlJson["Windows"]:
                        if (x["Room"]==r):
                            x["Actuator"]="H2O-"+r+"-linear"

                        
                    break

                    
                    
    if (balance and strategy!='constant'):
        print("Applying balance")
        controlJson["Balances"]={}
        controlJson["Balances"]["Global"]=allrooms
                    

    
    #json.dump(controlJson,open(controljson,'w'),indent=4)
    return controlJson

