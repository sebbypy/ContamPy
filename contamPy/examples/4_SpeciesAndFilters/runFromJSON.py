import os
import sys

currentPath = os.getcwd()

srcPath = os.path.join(currentPath,'..','..','src')

sys.path.append(srcPath)
sys.path.append(currentPath)

from caseManager import caseConfigurator,contamRunner


# Defining the paths of the various required ressources: reference building occupancy profiles, weather, libraries, contam EXE

ressourcesDir = os.path.join(currentPath,'..','Ressources')

refBuildingsDir = os.path.join(ressourcesDir,'RefBuildings')
occupancyDir = os.path.join(ressourcesDir,'OccupancyProfiles')
weatherDir = os.path.join(ressourcesDir,'Weather')
contaminantsDir = weatherDir
libraryDir = os.path.join(ressourcesDir,'CONTAM-Libraries')
contamDir = os.path.join(ressourcesDir,'CONTAM-Exe')


caseConfig = caseConfigurator(refBuildingsDir,occupancyDir,weatherDir,libraryDir,contaminantsDir)



# Parameters to apply to the system. The parameters listed here are the minimal required parameters

allParameters = {'building':'COVL-REN-RIJ2',
                'simulationType':'transient',
                 'v50':3,
                 'orientation':90,
                'system':{
                        'definition':'JSONfile',
                        'filename':'MHRV-RIJ2-BALANCED-FILTERS.json'
                        },
                'control':'systemJSONFile',
                'weather':'Uccle',
                'simulationTimeStep':'00:05:00',
                'StartDate':'Jan01',
                'EndDate':'Jan07',
                'outputTimeStep':'00:05:00',
                'outputFiles':['simconc','simflow','log','ach'],
                'shielding':'semi-exposed',
                'terrainRoughness':'III',
                'weatherRoughness':'I',
                }





# Read and apply parameters
caseConfig.readParameters(allParameters)




caseConfig.applyParameters()

caseConfig.addContaminant('PM2.5',20,0) # name of specie, default outside concentration , inside initial concentration. It will aslo add reports in each room
caseConfig.addContaminant('PM10',20,0) # name of specie, default outside concentration , inside initial concentration. It will aslo add reports in each room

caseConfig.writeContamFile('MHRV-RIJ2-BALANCED-FILTERS.prj')



# Run an existing PRJ file
contam = contamRunner(contamDir)    
contam.runContam('MHRV-RIJ2-BALANCED-FILTERS.prj')



import plotSpecies






