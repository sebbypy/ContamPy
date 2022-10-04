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


""" NB: this reference building should be reviewed to make sure the controls are named 
consistently with the latest approach"""


allParameters = {'building':'MaisonLimal-filled',
                 'simulationType':'transient',
                 'orientation':0,
                 'airTightness':{'v50':3,'leaksDistribution':'uniform'},
                 'system':{
                        'definition':'JSONfile',
                        'filename':'MHRV-And-VentilativeCooling.json'
                        },
                'control':{
                    'controlType': 'systemJSONFile'
                    },
                'occupancy':'default-home',
                'weather':'Uccle',
                'shielding':'semi-exposed',
                'terrainRoughness':'II',
                'weatherRoughness':'II',
                'simulationTimeStep':'00:05:00',
                'StartDate':'Jul01',
                'EndDate':'Jul31',
                'outputTimeStep':'00:05:00',
                'outputFiles':['simconc','simflow','log','ach'],
                'openStairs':True
                }



caseConfig.readParameters(allParameters)
caseConfig.applyParameters()
caseConfig.writeContamFile('MHRV-And-VentilativeCooling.prj')



# Run an existing PRJ file
contam = contamRunner(contamDir)    
contam.runContam('MHRV-And-VentilativeCooling.prj')

