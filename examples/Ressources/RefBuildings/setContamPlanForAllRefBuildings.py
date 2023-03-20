import os
import sys

currentPath = os.getcwd()

sys.path.append(os.path.join(currentPath,'..','..','..','src','planFunctions'))


from setContamPlan import setContamPlan


prjFilesWithoutDimensions = [x for x in os.listdir('modelsBeforeSetContamPlan') if '.prj' in x and '-bk' not in x]


for prjFile in prjFilesWithoutDimensions:
    
    print(prjFile)
    inputPRJ = os.path.join('modelsBeforeSetContamPlan',prjFile)

    outputPRJ = prjFile


    # This CSV file has to be filled by hand by the user from the "empty" one
    csvFileName = prjFile.replace('.prj','-areas-filled.csv')

    filledCSV =  os.path.join('modelsBeforeSetContamPlan',csvFileName)



    setContamPlan(inputPRJ,filledCSV,outputPRJ)
    



