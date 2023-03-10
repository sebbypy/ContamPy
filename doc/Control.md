# Control of ventilation systems

## Introduction

Control algorithms of ventilation systems can range from no control or very simple control to very complex local control involving sensors, weather, etc. 

The ventilation systems are described in a JSON file (see [BasicSimulation](BasicSimulation.md)). The control logic can be defined in the same file. 

## Concepts to define the control

The most adavanced possible control is a component per component control. Each of the components defined in the system JSON file can thus be controlled indivudually by an ***Actuator***

This actuator will be a the final control variable in Contam that is applied to the component. The term acutaor was chosen as it shomeshow refers to the physical component that control the flow rate of the opening of a component (control valve for example). 

The actuator (= control signal or variable) is generally the combination of a ***control algorithm*** that use one or more measured/monitored ***signals*** as input. 

Therefore, each individual component of the system JSON file can be controlled by an ***Actuator*** that combines a general ***ControlAlgorithm*** and one or more ***Signals***


## User inputs

The pieces of code shown below are based on the example case [examples/1d_runSystemFromJson_DemandControlled](../examples/1d_runSystemFromJson_DemandControlled)

To each component of the JSON file, one can add an actuator by its name

```
  "Mechanical exhaust": [
    {
      "Room": "Badkamer",
      "Nominal flow rate": 50,
      "Actuator": "H2O-Badkamer-linear"
    },
```

The actuator itself is defined as such in the ***Actuators*** section of the JSON file:

```
  "Actuators": {
    "H2O-Badkamer-linear": {
      "SignalName": "H2O-Badkamer",
      "ControlAlgorithmName": "H2O-Linear"
    },
```

It is thus well the combination of a signal and a control algorithm, that also have to be defined. 

The control algorithms are defined in the ***ControlAlgorithms*** section:

```
  "ControlAlgorithms": {
    "CO2-Linear": {
      "Type": "Linear",
      "Qmin": 0.1,
      "Qmax": 1.0,
      "Vmin": 500,
      "Vmax": 1000
    },
    "H2O-Linear": {
      "Type": "Linear",
      "Qmin": 0.1,
      "Qmax": 1.0,
      "Vmin": 0.3,
      "Vmax": 0.7
    },
```

The control algorithm H2O-Linear is itself defined by a "Type" and some parameters. The *Linear* type is an algorithm that makes the output vary between Qmin and Qmax for signal values between Vmin an Vmax (below or above the range, ouptut values are saturated). In this example, that means that the output signal will vary between 10% and 100% for relative humidity between 0.3  and 0.7 (if RH defined in 0-1 range). 

*Linear* is one of the types that is programmed in the source code of ContamPy. Other algoritms exist and are described further. New algorithms can be added on purpose. 

The ***SignalName*** is defined in the ***Signals*** section of the JSON file:
```
  "Signals": {
    "H2O-Badkamer": {
      "Type": "Single-Sensor",
      "Specie": "H2O",
      "Room": "Badkamer"
    },
	...,
    "Pres-WC": {
      "Type": "Presence",
      "Room": "WC"
    },
    "CO2-Slaapkamer3": {
      "Type": "Single-Sensor",
      "Specie": "CO2",
      "Room": "Slaapkamer3"
    },
```

There are several signal types. *Single-Sensor* gives the concentration of one specie defined in CONTAM in a given room. Other types of signals exist, such as *Presence* detection, which simply indicates if there is at least one occupant in the room. 



## Translation to CONTAM

There are several functions in ContamPy to transpose these inputs to CONTAM. A simple input such as a Linear control creates more than 10 CONTAM control nodes that are linked together with the required signals. 


## Description of available signals and control algorithms

***Important Note*** : the distinction between signals, algorithms and actuators is quite clear on paper, but may be a little less absolute in practice. See for example the "Clock" or "IsBetween" control algorithms. 
The initial implementation had only one control signal possible for an algorithm, while some algorithms require more than one.
Some changes in the input format are thus to be expected in the future. 


### Signals

The currently available signals are:

***Single-Sensor***

Species sensors

```
    "CO2-Slaapkamer3": {
      "Type": "Single-Sensor",
      "Specie": "CO2",
      "Room": "Slaapkamer3"
    },
```

***Max-Sensors***

```
    "CO2-Max": {
      "Type": "Max-Sensors",
      "Specie": "CO2",
      "Room": ["Room1","Room2"]
    },
```


***Single-TSensor***

Temperature sensors
```
   "TGarage": {
      "Type": "Single-TSensor",
      "Room": "Garage"
    }
```

***Presence***
```
 "Pres-WC": {
      "Type": "Presence",
      "Room": "WC"
    },
```

***Clock***

```
 "DayClock": {
      "Type": "Clock",
      "Schedule": {
        "00:00:00": 0.1,
        "08:00:00": 1.0,
        "22:00:00": 0.1,
        "24:00:00": 0.1
      }
    }
```

***Collector***

WARNING: this makes a mass flow weighted average depending on the extract flow rates of target rooms. That means that there should be a non-zero mechanical extract in the listed rooms. 

```
   "CO2-collector": {
      "Type": "Collector",
      "Specie": "CO2",
      "Rooms": ["Room1","Room2"]
    }
```


### Control algoritms 

***Linear***

Output varies between Qmin and Qmax for an input varying between Vmin and Vmax. If input < Vmin, output = Qmin, if input < Vmax, ouput = Qmax.

```
 "H2O-Linear": {
      "Type": "Linear",
      "Qmin": 0.1,
      "Qmax": 1.0,
      "Vmin": 0.3,
      "Vmax": 0.7
    }
```

***Timer***

Typically used for toilet for example, with presence as input signal. 

Output is Qmin if input is 0. 

Output switches to Qmax when input signal is 1. 

When input signal switches back to 0, output stays Qmax during the defined duration. 

```  "Timer30min": {
      "Type": "Timer",
      "Qmin": 0.1,
      "Qmax": 1,
      "Duration": "30min"
    },
```
Duration can be expressed as minutes ("10min" format) or hours ("1H" or "1h" format)

***Clock***

Control schedule in a similar fashion as in ContamW. 

```
"DayClock": {
  "Type": "Clock",
  "Schedule": {
    "00:00:00": 0.1,
    "08:00:00": 1.0,
    "22:00:00": 0.1,
    "24:00:00": 0.1
  }
},
```

Obviously, when using a clock algorithm, no signal is needed when defining an actuator

``` 
"ConstantClockActuator": {
      "SignalName": "",
      "ControlAlgorithmName": "DayClock"
    }
````

***GreatherThan***
```
"GreaterThan25": {
    "Type": "GreaterThanValue",
    "Value": 25
}
```

***IsBetween***

This algorithm has no input parameters, but has 3 input signals. Lower and upper limits will be defined at the actuator level.

It returns 1 if the input signal is between the lower and upper signal, 0 otherwise. 

```
"BetweenAlgo":{
   "Type":"IsBetween"
}
```

```
"BetweenActuator":{
    "ControlAlgorithmName": "BetweenAlgo",
	"SignalName": "Temp-Woonkamer",
	"LowerValue": "Temp-Ext
	"UpperValue": "Temp-Attic"
}
```



