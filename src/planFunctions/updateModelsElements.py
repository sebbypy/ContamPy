import sys
import os

dirPath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dirPath,'..','contamFunctions'))


import contam_functions

import shutil


def updateModelsElements(inputProjectFile):


    referenceEmptyFileName = os.path.join(dirPath,'empty_model.prj')
    referenceContamModel = contam_functions.loadcontamfile(referenceEmptyFileName)
    referenceFlowElements = referenceContamModel['flowelems']


    contam_data=contam_functions.loadcontamfile(inputProjectFile)
    contam_data['flowelems'] = referenceFlowElements
    
 
    backupFileName =    inputProjectFile.replace('.prj','-bk.prj')
 
    shutil.copyfile(inputProjectFile,backupFileName)

    
    contam_functions.writecontamfile(backupFileName,inputProjectFile,contam_data)


