# ContamPy
Python scripts and tools to set up and run ***CONTAM*** models

The purpose of this library is to ease and speed-up the setup of CONTAM simulations through Python. 

## Context and driving principles in the development of ContamPy

As a regular and advanced user of both CONTAM and programming languages (especially Python), I had the impression that it could be easier and less time consuming to set-up CONTAM simulations. 

After using it for a while and writing a lot of scripts to automate some tasks, making some parametric analyses or postprocessing routines, I came to the conclusion that it would be more userful and more efficient to develop something more ambitious and to setup (almost) the whole model in Python.

Here are some of the thoughts that have driven the development:

+ The Contam GUI has features than can hardly be replaced by Python scripts (excepted if developing a new GUI - which has never been the target)
	+ drawing the layout (floor plans) of the building
	+ easy positioning of the flow paths on the plan, with the implicit definition of the flow paths azimuth
	+ visualization of the direction of flow and pressure differences in postprocessing
+ All the rest would be easier/faster to defined in scripts or files, especially controls
+ The readability of the model is poor from the perspective of a ventilation engineer:
	+ characteristics of the ventilation system are spread all over the file (flow elements, flow paths, controls, ...)
	+ the way flow elements are formulated is rather mathematical (powerlaw, exponents, orifice areas, one-way flow or two-way flow). I rather use flow rates, v50 or   I work rates, flow capacities at a given pressure, n50 or v50 than with powerlaws, vent capacity, open door, etc. 


As a consequence, ContamPy has been developed following principles
+ the building layout and flow paths have still to be drawn and positioned in the building using ContamW, but all other data should be defined from external files and/or scripts
+ except the building data all the rest should be programmed or automated so that it is very quick to set up a model or to make changes
+ description of a ventilation system should be more field oriented and human readable




## Quick start guide

A lot of examples are given in the folder [examples](examples) showing all the capabilities of ContamPy

A few of them are highlighted below with detailled explanations of the key concepts and functions. 

***Drawing a ContamPy compatible building and set its dimensions***

[Example files](examples/0_modelGeneration/) - [Detailled explanation](doc/DrawBuilding.md)

***First simulation and definition of ventilation system***

[Example files](examples/1_runSystemFromJson/) - [Detailled explanation](doc/BasicSimulation.md)

***Control of the ventilation system***

[Example files](examples/1d_runSystemFromJson_DemandControlled/) - [Detailled explanation](doc/Control.md)



<!--***Adding controls***

[Example files with simple clock control](examples/1c_runSystemFromJson_ClockControl/)

[Example files with sensors and demand control ventilation](examples/1d_runSystemFromJson_DemandControlled/)

[Detailled guide](doc/Controls.md)
-->


