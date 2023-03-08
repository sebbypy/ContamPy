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




allParameters = {'building':'COVL-REN-RIJ2',
                'simulationType':'transient',
                 'airTightness':{'v50':3,'leaksDistribution':'uniform'},
                 'orientation':90,
                 'system':{
                        'definition':'JSONfile',
                        'filename':'MHRV-RIJ2-BALANCED.json'
                        },
                'control':{
                        'controlType':'systemJSONFile'
                        },
                'weather':'Uccle',
                'contaminants':{
                    'HCHO':{
                        "unit": "ug/m3",
                        "initialConcentration": 10,
                        "outsideConcentration": 1,
                        "source":{
                            "type":"constantRatePerFloorArea",
                            "rate": 100,
                            "unit": "ug/h"}
                        },
                    'FIC':{
                        "unit": "ug/m3",
                        "initialConcentration": 1,
                        "outsideConcentration": 0,
                        "source":{
                            "type":"constantRatePerTotalArea",
                            "rate": 1,
                            "unit": "ug/h"}
                        },
                    'PM2.5':{
                        "unit": "ug/m3",
                        "initialConcentration": 0,
                        "outsideConcentration": 25
                        }
                    },
                'simulationTimeStep':'00:05:00',
                'StartDate':'Jan01',
                'EndDate':'Jan07',
                'occupancy':'default-home',
                'outputTimeStep':'00:05:00',
                'outputFiles':['simconc','simflow','log','ach'],
                'shielding':'semi-exposed',
                'terrainRoughness':'III',
                'weatherRoughness':'I',
                }





# Read and apply parameters
caseConfig.readParameters(allParameters)
caseConfig.applyParameters()



caseConfig.writeContamFile('MHRV-RIJ2-BALANCED.prj')



# Run an existing PRJ file
contam = contamRunner(contamDir)    
contam.runContam('MHRV-RIJ2-BALANCED.prj')



import plotSpecies






