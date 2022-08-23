import os
import sys

currentPath = os.getcwd()
sys.path.append(os.path.join(currentPath,'..','..','src'))
sys.path.append(os.path.join(currentPath,'..','..','src','postProcessing'))

from caseManager import caseConfigurator,contamRunner

from postpro_functions import getBlowerDoorResults


# Defining the paths of the various required ressources: reference building occupancy profiles, weather, libraries, contam EXE

ressourcesDir = os.path.join(currentPath,'..','Ressources')

refBuildingsDir = os.path.join(ressourcesDir,'RefBuildings')
occupancyDir = os.path.join(ressourcesDir,'OccupancyProfiles')
weatherDir = os.path.join(ressourcesDir,'Weather')
contaminantsDir = weatherDir
libraryDir = os.path.join(ressourcesDir,'CONTAM-Libraries')
contamDir = os.path.join(ressourcesDir,'CONTAM-Exe')


caseConfig = caseConfigurator(refBuildingsDir,occupancyDir,weatherDir,libraryDir,contaminantsDir)




v50 =1

allParameters = {'building':'COVL-REN-RIJ2',
                'simulationType':'blowerDoor',
                'v50':v50,
                'outputFiles':['simconc','simflow','log','ach'],
                }




# Read and apply parameters, writing the resulting contam file
caseConfig.readParameters(allParameters)
caseConfig.applyParameters()
caseConfig.writeContamFile('BlowerDoor.prj')


# Run an existing PRJ file
contam = contamRunner(contamDir)    
contam.runContam('BlowerDoor.prj')




#getting blower door results
leaks = caseConfig.getLeaksInformations()

blowerDoorResults = getBlowerDoorResults('BlowerDoor.val')


n50 = blowerDoorResults['Volume flow rate (m3/h)']/blowerDoorResults['Conditioned volume']


print("Sum of leaks multipliers in the CONTAM model (should be equal to v50*(total area) ): "+str(leaks.loc['Total','v50*area']))
print("v50: ",v50)
print("Resulting area: ",leaks.loc['Total','v50*area']/v50)
for k,v in blowerDoorResults.items():
    print(k+": "+str(v))
print("n50 :","{:.1f}".format(n50))



