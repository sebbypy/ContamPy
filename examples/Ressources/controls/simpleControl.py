import copy

"""
Example of simple control applied to a MEV case

Humidity control in exhaust rooms:
    linear variation of flow rate between 10% and 100% for humidity varying from 30% to 70%
      
Exception for the toilet:
    switch between 10% and 100% of nominal flow rate based on presence detection
    there is a timer: the flow remains 100% for 30minutes after the latest occupancy
   
"""

    

def compute(**kwargs):
    
    systemJson = kwargs['systemJson']  
    controlJson = copy.deepcopy(systemJson)

    controlJson["ControlAlgorithms"]={}
    controlJson["Signals"]={}    
    controlJson["Actuators"]={}



    # defining global algorithms 

    minFlow = 0.1
    maxFlow = 1.0

    refalgos={
        "H2O-Linear":
            {"Type":"Linear","Qmin":minFlow,"Qmax":maxFlow,"Vmin":0.3,"Vmax":0.7},
        "Timer30min":
            {"Type":"Timer","Qmin":minFlow,"Qmax": maxFlow,"Duration": "30min"}
        }
    controlJson["ControlAlgorithms"]=refalgos



    # creating signals and actuators

    exhaustrooms=[ x["Room"] for x in controlJson["Mechanical exhaust"] ]

    for room in exhaustrooms:
   
        if (room=='WC'):
            signaldict={'Type':'Presence','Room':room}

            signalName = "Pres-WC"
            actuatorName = "WC-Timer"
            
            controlJson["Signals"][signalName]=signaldict
            
            actuatordict={"SignalName":signalName,"ControlAlgorithmName":"Timer30min"}

            controlJson["Actuators"][actuatorName]=actuatordict

            for x in controlJson["Mechanical exhaust"]:
                if (x["Room"]==room):
                    x["Actuator"]=actuatorName

        else:
             
            
            signaldict={"Type":"Single-Sensor","Specie":"H2O","Room":room}

            signalName = "H2O-"+room
            actuatorName = "H2O-"+room+"linear"

            controlJson["Signals"]["H2O-"+room]=signaldict

            actuatordict={"SignalName":signalName,"ControlAlgorithmName":"H2O-Linear"}

            controlJson["Actuators"][actuatorName]=actuatordict

            for x in controlJson["Mechanical exhaust"]:
                if (x["Room"]==room):
                    x["Actuator"]=actuatorName

                

    return controlJson

