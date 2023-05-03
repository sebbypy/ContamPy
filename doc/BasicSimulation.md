# Running a simulation: main script and JSON description of a ventilation system

## Main script description

Running a Contam case with ContamPy requires:
+ to import/load a certain number of modules or python files
+ define some folders where ressources (weather file, building file, ect) can be founda simulation requires to define several parameters
+ define simulation parameters and apply them in a PRJ file
+ execute Contam

The file [runFromJSON.py](../examples/1_runSystemFromJson/runFromJSON.py) of example [1_runSystemFromJson](../examples/1_runSystemFromJson) is detailled in this section.

***Import modules***

```
import os
import sys

currentPath = os.getcwd()
sys.path.append(os.path.join(currentPath,'..','..','src'))

from caseManager import caseConfigurator,contamRunner
```

caseConfigurator is the main class that will be used to configure the Contam project. 

contamRunner is a wrapper class that will call and execute the Contam Executable. 


***Define various paths where ressources will be found***

```
ressourcesDir = os.path.join(currentPath,'..','Ressources')

refBuildingsDir = os.path.join(ressourcesDir,'RefBuildings')
occupancyDir = os.path.join(ressourcesDir,'OccupancyProfiles')
weatherDir = os.path.join(ressourcesDir,'Weather')
contaminantsDir = weatherDir
libraryDir = os.path.join(ressourcesDir,'CONTAM-Libraries')
contamDir = os.path.join(ressourcesDir,'CONTAM-Exe')


caseConfig = caseConfigurator(refBuildingsDir,occupancyDir,weatherDir,libraryDir,contaminantsDir)
```

***Define the main parameters of the simulation, applying them to the buidling, writing the final PRJ file***

```
allParameters = {'building':'SingleZone',
                'simulationType':'transient',
                'system':{
                        'definition':'JSONfile',
                        'filename':'simpleSystem.json'
                        },
                'weather':'Uccle',
                'simulationTimeStep':'00:05:00',
                'StartDate':'Jan01',
                'EndDate':'Jan07',
                'outputTimeStep':'00:05:00',
                'outputFiles':['simconc','simflow','log','ach'],
                }

caseConfig.readParameters(allParameters)
caseConfig.applyParameters()
caseConfig.writeContamFile('simpleModel.prj')
```

The dictionnary *allParameters* implicitely refers to some of the above ressources:
+ The file *SingleZone.prj* is expected to be in the *refBuildingsDir* folder (in this example, this means [examples/Ressources/RefBuildings](../examples/Ressources/RefBuildings))
+ The weather file *Uccle.wth* is expected to be in the *weatherDir* folder (in this example, this means [examples/Ressources/Weather](../examples/Ressources/Weather))

The ventilation system is described in a JSON file [simpleSystem.json](../examples/1_runSystemFromJson/simpleSystem.json). Its syntax is explained below. 


## Description of the ventilation system in a JSON file

### Introduction

There are several reasons that lead to the choice the ***JSON*** format to define the ventilation system:
+ It's human readable and the whole system is described in a single place (in a CONTAM file, one must look at several items and places to understand the system that is modeled)
+ One can define a custom format that is very explicit and closer to the field (using flow rates, design pressure and flow capacities is much more explicit than the coefficients of a powerlaw...)
+ It's easy to load, save or modify in Python (or any other software)


### Description of main components

***Mechanical supply or exhaust***

This first example is very basic, and the whole JSON file is very short:
```
{
  "Mechanical supply": [
    {
      "Room": "Woonkamer",
      "Nominal flow rate": 50
    }
  ],
  "Mechanical exhaust": [
    {
      "Room": "Woonkamer",
      "Nominal flow rate": 45
    }
  ],
  "Natural supply": [],
  "Natural exhaust": [],
  "Natural transfer": []
}
```

The mechanical supply or exhaust are simply defined by a nominal flow rate (expressed in ***m³/h***) for each room. 

A more complex system (for a more complex building) is given in [examples/1b_runSystemFromJson_MoreComplex/MEV-RIJ2.json](../examples/1b_runSystemFromJson_MoreComplex/MEV-RIJ2.json). 

There is no Mechanical supply (it is a MEV system), but 4 exhausts of 50, 50,50, and 25 m³/h in the different zones. 

```
  "Mechanical supply": [],
  "Mechanical exhaust": [
    {
      "Room": "Badkamer",
      "Nominal flow rate": 50
    },
    {
      "Room": "Wasplaats",
      "Nominal flow rate": 50
    },
    {
      "Room": "Keuken",
      "Nominal flow rate": 50
    },
    {
      "Room": "WC",
      "Nominal flow rate": 25
    }
  ],
```

***Natural supply vents***

The natural supply vents are defined by a capacity (flow rate in m³/h) and a design pressure. This means that this flow path will deliver this flow rate for the design pressure. 

In the background (in CONTAM), natural supply vents are simply power law components whose parameters are calculated to meet these properties (assuming a 0.5 exponent).

If the "Self-Regulating" flag is set to "Yes", the self-regulating vent model of CONTAM is used. For now, the flow is saturated to 1.5 the design flow, but it could be added as a parameter in the future.

```
  "Natural supply": [
    {
      "Room": "Slaapkamer3",
      "Capacity": 25,
      "Design pressure": 2,
      "Self-Regulating": "No"
    },
    {
      "Room": "Slaapkamer2",
      "Capacity": 25,
      "Design pressure": 2,
      "Self-Regulating": "No"
    },
```

***Natural transfer between rooms***

Natural transfer between rooms is generally insured by spefic wall or door mounted grids, or by door slits. Just as the natural supply vents, they are defined by a cacpacity (in m³/h) and a design Pressure. They are generally no movable parts, so there is no "Self-Regulating" flag. 

```
  "Natural transfer": [
    {
      "From room": "Nachthal2",
      "To room": "Slaapkamer3",
      "Capacity": 25,
      "Design pressure": 2
    },
    {
      "From room": "Nachthal2",
      "To room": "Slaapkamer2",
      "Capacity": 25,
      "Design pressure": 2
    },
```

### Additional remarks

The mechanical supply or exhaust flow rates will be used to define the design flow rate of supply or extract points in the CONTAM project file. Of course, no flow rate is defined for most of the spaces, and their flow rate will thus remain 0. 

The natural components design pressure (vents or openings bewteen rooms) and capacities will be translated to power law (of self-regulating vent) models with appropriate coefficients. Of course, it is only possible to define a natural transfer between two rooms if there exist a flow path between the two rooms in the CONTAM project. Otherwise, the code will generate an error. 



### List of components and hypotheses

| Component name                      | Short notation | Type          | Inputs                                                                     | Underlying Contam model            | Assumptions or modelling tricks                                                                                                                            |
|-------------------------------------|----------------|---------------|----------------------------------------------------------------------------|------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Natural supply                      | NSV            | From exterior | Design pressure (Pa)<br> Capacity (m³/h) <br> Preferred orientation (degrees)       | Powerlaw Model: Q = C(dP)^n        | n = 0.5                                                                                                                                                    |
| Self-regulating natural supply vent | SR_NSV         | From exterior | Design pressure (Pa)<br> Capacity (m³/h) <br> Preferred orientation (degrees)       | Self-regulating Vent Model         | Q0 = 1.5 * Capacity dp0 computed to have the design capacity at the design pressure                                                                        |
| Ventilative cooling component       | VCC            | From exterior | Discharge coefficient (-)<br>Area (m²)<br>referred orientation (degrees)        | Powerlaw Model: Q = C(dP)^n        | As they are mainly designed for cross ventilation, assuming one way flow component.                                                                        |
| Normal window (wall mounted)        | NW             | From exterior | Width (m)<br>Height (m)<br>Preferred orientation (degrees)                       | Two-way Flow Model: Single Opening | Cd = 0.6                                                                                                                                                   |
| Roof window (with slope)            | RW             | From exterior | Width (m)<br> Height (m)<br>Inclination (degrees)<br>Preferred orientation (degrees) | Two-way Flow Model: Single Opening | Cd = 0.6 Correction of height and width to have the correct stack  effect and to keep the correct area: h’ = h*sin(inclindation) w’ = w/sin(inclination)   |
| Natural transfer opening            | NT             | Between rooms | Design pressure (Pa)<br>Capacity (m³/h)                                       | Powerlaw Model: Q = C(dP)^n        | n = 0.5                                                                                                                                                    |
| Open door                           | OD             | Between rooms | -                                                                          | Powerlaw Model: Q = C(dP)^n        | n = 0.5 Cd = 0.6 Introduced to test the sensitivity of systems to low internal resistance                                                                  |






<!--


# Run an existing PRJ file
contam = contamRunner(contamDir)    
contam.runContam('simpleModel.prj')

-->