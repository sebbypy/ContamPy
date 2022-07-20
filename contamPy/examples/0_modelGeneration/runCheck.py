import os
import sys

currentPath = os.getcwd()

sys.path.append(os.path.join(currentPath,'..','..','planFunctions'))


from checkContamPlan import checkContamPlan

inputPRJ = 'DetachedHouse_noDimensions.prj'


checkContamPlan(inputPRJ)


