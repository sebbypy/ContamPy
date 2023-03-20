import os 
import sys

currentPath = os.getcwd()

sys.path.append(os.path.join(currentPath,'..','..','..','..','src','planFunctions'))


from updateModelsElements import updateModelsElements


#inputPRJ = 'SingleZone.prj'
inputPRJ = 'COVL-REN-RIJ2.prj'

updateModelsElements(inputPRJ)