import os
import sys

currentPath = os.getcwd()
sys.path.append(os.path.join(currentPath,'..','..','src'))

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
                        'filename':'MEV-RIJ2.json'
                        },
                'weather':'Uccle',
                'simulationTimeStep':'00:05:00',
                'StartDate':'Jan01',
                'EndDate':'Jan07',
                'outputTimeStep':'00:05:00',
                'outputFiles':['simconc','simflow','log','ach'],
                'shielding':'exposed',
                'terrainRoughness':'III',
                'weatherRoughness':'I',
                }




# Read and apply parameters, writing the resulting contam file
caseConfig.readParameters(allParameters)
caseConfig.applyParameters()
caseConfig.writeContamFile('MEV-RIJ2.prj')



# Run an existing PRJ file
contam = contamRunner(contamDir)    
contam.runContam('MEV-RIJ2.prj')

