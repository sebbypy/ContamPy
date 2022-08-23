import os
import sys

currentPath = os.getcwd()


sys.path.append(os.path.join(currentPath,'..','..','src','planFunctions'))


from checkContamPlan import checkContamPlan

inputPRJ = 'houseWithSlopedRoofNoDim.prj'



checkContamPlan(inputPRJ)


