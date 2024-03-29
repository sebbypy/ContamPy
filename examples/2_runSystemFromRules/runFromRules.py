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

namedSystemsDirectory = os.path.join(ressourcesDir,'namedSystems')


caseConfig = caseConfigurator(refBuildingsDir,occupancyDir,weatherDir,libraryDir,contaminantsDir,namedSystemsDirectory)



# Parameters to apply to the system. The parameters listed here are the minimal required parameters

allParameters = {'building':'COVL-REN-RIJ2',
                'simulationType':'transient',
                 'airTightness':{'v50':3,'leaksDistribution':'uniform'},
                 'orientation':90,
                'system':{
                        'definition':'namedSystem',
                        'name':'simpleMEV'
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

#saving the json file
caseConfig.writeCurrentJSON('MEV-RIJ2-namedSystem.json')

caseConfig.writeContamFile('MEV-RIJ2-namedSystem.prj')



# Run an existing PRJ file
contam = contamRunner(contamDir)    
contam.runContam('MEV-RIJ2-namedSystem.prj')

