# ContamPy
Python scripts and tools to set up and run ***CONTAM*** models

The purpose of this library is to ease and speed-up the setup of CONTAM simulations through Python. The graphical user interface Contam***W*** is nice, but its use is quite time-consuming, especially for drawing control networks. Furthermore, doing parametric analyses is not straightforward through the GUI. 

## Driving principles in the development of ContamPy

+ The ContamW GUI has features than can hardly be replaced by Python scripts (without developing a new GUI)
	+ drawing the layout (floor plans) of the building
	+ putting flow paths at the right place, with the implicit definition of the flow paths azimuth
	+ visualize the direction of flow and pressure differences
+ All the rest is easier/faster to defined in scripts or files
+ The way to define flow elements or flow paths is not close enough to the ventilation field





## Quick start guide

***Drawing a ContamPy compatible building and set its dimensions***

[Example files](examples/0_modelGeneration/) - [Detailled explanation](doc/DrawBuilding.md)

***First simulation and definition of ventilation system***

[Example files](examples/1_runSystemFromJson/) - [Detailled explanation](doc/BasicSimulation.md)


<!--***Adding controls***

[Example files with simple clock control](examples/1c_runSystemFromJson_ClockControl/)

[Example files with sensors and demand control ventilation](examples/1d_runSystemFromJson_DemandControlled/)

[Detailled guide](doc/Controls.md)
-->


