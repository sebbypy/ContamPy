import os
import sys

currentPath = os.getcwd()

sys.path.append(os.path.join(currentPath,'..','..','src','planFunctions'))


from setContamPlan import setContamPlan

inputPRJ = 'DetachedHouse_noDimensions.prj'

outputPRJ = 'DetachedHouse_withDimensions.prj'


# This CSV file has to be filled by hand by the user from the "empty" one
filledCSV = 'DetachedHouse_noDimensions-areas-filled.csv'


setContamPlan(inputPRJ,filledCSV,outputPRJ)
    



