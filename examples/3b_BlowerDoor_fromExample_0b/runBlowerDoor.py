import os
import sys

currentPath = os.getcwd()
sys.path.append(os.path.join(currentPath,'..','..','src'))
sys.path.append(os.path.join(currentPath,'..','..','src','postProcessing'))

from caseManager import caseConfigurator,contamRunner

from postpro_functions import getBlowerDoorResults


# Defining the paths of the various required ressources: reference building occupancy profiles, weather, libraries, contam EXE

ressourcesDir = os.path.join(currentPath,'..','Ressources')

occupancyDir = os.path.join(ressourcesDir,'OccupancyProfiles')
weatherDir = os.path.join(ressourcesDir,'Weather')
contaminantsDir = weatherDir
libraryDir = os.path.join(ressourcesDir,'CONTAM-Libraries')
contamDir = os.path.join(ressourcesDir,'CONTAM-Exe')


refBuildingsDir = os.path.join(currentPath,'..','0b_modelGenerationSlopedRoof')


caseConfig = caseConfigurator(refBuildingsDir,occupancyDir,weatherDir,libraryDir,contaminantsDir)


v50 =3



if not os.path.exists(os.path.join(refBuildingsDir,'houseWithSlopedRoofWithDimensions.prj')):
    print ("File houseWithSlopedRoofWithDimensions.prj does not exist in example 0b") 
    print("Please run example 0b first before trying the present one")
    raise ValueError("Run example 0b before running this one")



allParameters = {'building':'houseWithSlopedRoofWithDimensions',
                'simulationType':'blowerDoor',
                'airTightness':{'v50':v50,'leaksDistribution':'uniform'},
                'outputFiles':['simconc','simflow','log','ach'],
                }

caseConfig.readParameters(allParameters)
caseConfig.applyParameters()
caseConfig.writeContamFile('houseWithSlopedRoofWithDimensions-blowerDoor.prj')


# Run an existing PRJ file
contam = contamRunner(contamDir)    
contam.runContam('houseWithSlopedRoofWithDimensions-blowerDoor.prj')




#getting blower door results
leaks = caseConfig.getLeaksInformations()


blowerDoorResults = getBlowerDoorResults('houseWithSlopedRoofWithDimensions-blowerDoor.val')


n50 = blowerDoorResults['Volume flow rate (m3/h)']/blowerDoorResults['Conditioned volume']


print("Sum of leaks multipliers in the CONTAM model (should be equal to v50*(total area) ): "+str(leaks.loc['Total','v50*area']))
print("v50: ",v50)
print("Resulting area: ",leaks.loc['Total','v50*area']/v50)
for k,v in blowerDoorResults.items():
    print(k+": "+str(v))
print("n50 :","{:.1f}".format(n50))



