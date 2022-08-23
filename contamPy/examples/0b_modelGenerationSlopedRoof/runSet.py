import os
import sys

currentPath = os.getcwd()

sys.path.append(os.path.join(currentPath,'..','..','src','planFunctions'))


from setContamPlan import setContamPlan

inputPRJ = 'houseWithSlopedRoofNoDim.prj'

outputPRJ = 'houseWithSlopedRoofWithDimensions.prj'


# This CSV file has to be filled by hand by the user from the "empty" one
filledCSV = 'houseWithSlopedRoofNoDim-areas-filled.csv'


setContamPlan(inputPRJ,filledCSV,outputPRJ)
    

