import os
import sys
import importlib
import subprocess


dirPath = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.join(dirPath,'contamFunctions'))
sys.path.append(os.path.join(dirPath,'computeFunctions/systems'))
sys.path.append(os.path.join(dirPath,'computeFunctions/controls'))
sys.path.append(os.path.join(dirPath,'setFunctions'))
sys.path.append(os.path.join(dirPath,'tools'))



import contam_functions
import setSystem,setControls,setOccupancyAndSources,setBCS,setWeatherAndOutputs
import computeControls


class caseConfigurator:

    
    def __init__(self,templatesDir,dimBuildingsDir):
       
        self.defaultParameters={'building':'COVL-REN-HO1',
                                'orientation':0,
                                'v50':3,
                                'system':'DPREVENT',
                                'control':'constant',
                                'occupancy':'default-home',
                                'weather':'Uccle'
                                }
        
        self.actualParameters=self.defaultParameters.copy()

        self.templatesDir = templatesDir
        self.dimBuildingsDir = dimBuildingsDir
    
        self.ContamModel = None



    def configureSimulation(self,parametersDict,outputFileName):

        self.areParametersValid(parametersDict)

        self.getBuildingModel()

        systemJSON = self.computeSystem()        
        self.setSystem(systemJSON)
        
        controlJSON = self.computeControl(systemJSON)     
        self.setControls(controlJSON)

        self.setOccupancyAndSources()

        self.setAirtightnessOrientation()
        
        self.setWeatherAndOuputs()
        
        self.writeContamFile(outputFileName)
        

    def areParametersValid(self,parametersDict):
              
        for key in parametersDict.keys():
            
            if key not in self.defaultParameters.keys():
                
                print("Unknown argument ",key)
                exit()
    
            else:
                self.actualParameters[key]=parametersDict[key]
    

    def getBuildingModel(self):
        
        self.baseFileName = os.path.join(self.dimBuildingsDir,self.actualParameters['building']+'.prj')
        self.ContamModel = contam_functions.loadcontamfile(self.baseFileName)



    def writeContamFile(self,outputFileName):
        
        #def writecontamfile(reffile,newname,datadict):
        finalFileName = os.path.join(os.getcwd(),outputFileName)
       
        contam_functions.writecontamfile(self.baseFileName,finalFileName,self.ContamModel)


    def computeSystem(self):
        
        system=self.actualParameters['system']

        systemComputeFunction,systemArgs = existingSystems().functionAndArguments(system)

        allArguments = [self.ContamModel] + systemArgs

   
        json = systemComputeFunction(allArguments)

        return json


    def setSystem(self,systemJson):
        
        setSystem.apply(self.ContamModel,systemJson)
        

    def computeControl(self,systemJson):
        
        controlStrategy=self.actualParameters['control']

        controlJson = computeControls.compute([systemJson,controlStrategy])

        return controlJson


    def setControls(self,controlJson):
        
        setControls.setControls(self.ContamModel,controlJson)


    def setOccupancyAndSources(self):

        occupancy = self.actualParameters['occupancy']
        
        setOccupancyAndSources.apply(self.ContamModel,occupancy,self.templatesDir)
        

    def setAirtightnessOrientation(self):
        
        v50= self.actualParameters['v50']
        orientation = self.actualParameters['orientation']
        
        setBCS.apply(self.ContamModel,v50,orientation)
        
    def setWeatherAndOuputs(self):
        
        weather = self.actualParameters['weather']        
        weatherFile = os.path.join(self.templatesDir,'Weather',weather+'.wth')
        
        setWeatherAndOutputs.apply(self.ContamModel,weatherFile)




class contamRunner:
    
        def __init__(self,contamExeDir):
            
            self.contamExe = os.path.join(contamExeDir,'contamx3.exe')
    
        def runContam(self,prjFile):

            #prjFileRelative = self.makePrjRelative(prjFile)
            
            prjFileRelative = os.path.relpath(prjFile)


            #seems the file name should not be too long otherwise contam do noting --> should use relative path  for the file! 
            #I dont know why but the output of contam is on stderr and not stdout --> catching stderr
            completedProcess=subprocess.run([self.contamExe,prjFileRelative],stderr=subprocess.PIPE)
       
            stdoutFileName = prjFile.replace('.prj','.console')
            f=open(stdoutFileName,'w')
            f.write(completedProcess.stderr.decode())
            f.close()

        def makePrjRelative(self,prjFile):
            
            workingDir = os.getcwd()
            
            prefixToRemove = os.path.commonpath([workingDir,prjFile])
            
            prjFileRelative = prjFile.replace(prefixToRemove,'')

            print(prjFileRelative)

            return prjFileRelative


class existingSystems:
    
    def __init__(self):
        
        self.systems={
                    'CNBN':{
                            'file':'compute_NBN_D50_001',
                            'arguments':['C']
                            },
                    'DNBN':{
                            'file':'compute_NBN_D50_001',
                            'arguments':['D','auto-balance-prop']
                            },
                    'CNBNSLAAP':{
                            'file':'compute_NBN_D50_001',
                            'arguments':['C','extract-slaapkamers']
                            },
                    'CPREVENT':{
                            'file':'compute_PREVENT',
                            'arguments':['C','auto-balance-prop']
                            },
                    'DPREVENT':{
                            'file':'compute_PREVENT',
                            'arguments':['D','auto-balance-prop']
                            },
                    'CSLAAPPREVENT':{
                            'file':'compute_PREVENT',
                            'arguments':['CSLAAP']
                            },
                    'CSupplyHall':{
                            'file':'compute_PREVENT',
                            'arguments':['CsupplyHall']
                            },
                    'Windows':{
                            'file':'compute_SingleSidedWindows',
                            'arguments':[]}                          
                          
                    }
        
    def functionAndArguments(self,system):
                       
        systemModule = importlib.import_module(self.systems[system]['file'])        
        
        return systemModule.compute,self.systems[system]['arguments']





        

class ClassConfiguratorTester():
    
    
    def __init__(self,logFileName,templatesDir,buildingsDir):

        self.baseCaseParameters={'building':'COVL-REN-HO1',
                                 'orientation':35,
                                 'v50':6,
                                 'system':'CNBNSLAAP',
                                 'control':'fulllocal',
                                 'occupancy':'default-active'
                                 }   
    
        self.parametersRanges={'building':
                                ['COVL-REN-HO1',
                                 'COVL-REN-HO2',
                                 'COVL-REN-VRIJ1',
                                 'COVL-REN-VRIJ2',
                                 'COVL-REN-RIJ1',
                                 'COVL-REN-VRIJ2'],
                             'system':
                                 list(existingSystems().systems.keys()),
                             'control':
                                 ['fullocal','constant'],
                             'occupancy':
                                 ['default-home','default-active']
                             }
    
        
        self.logFileName = logFileName
        self.templatesDir = templatesDir
        self.buildingsDir = buildingsDir
            
            
    def startTestLog(self):
            
        self.originalStdout = sys.stdout
        self.originalStderr = sys.stderr
        self.logfile = open(self.logFileName,'w')
        sys.stdout = self.logfile
        sys.stderr = self.logfile


    def stopTestLog(self):
        
        sys.stdout = self.originalStdout
        sys.stderr = self.originalStderr

        self.logfile.close()
        
    
    def testSingleParameterVariations(self):
        
        self.startTestLog()
        
        failedTests=[]
        
        for parameterName in self.parametersRanges.keys():
            
            for parameterValue in self.parametersRanges[parameterName]:
        
                caseParameters=self.baseCaseParameters.copy()
                
                caseParameters[parameterName]=parameterValue
            
                try:
                    print("Testing ",caseParameters)
                    caseConfigurator(self.templatesDir,self.buildingsDir).configureSimulation(caseParameters,'test.prj')
                    os.remove('test.prj')

                except:
                    
                    print("Test failed for parameter set ",caseParameters)
                    failedTests.append(caseParameters)


        self.stopTestLog()
    
        #console print    
        print("Number of failed tests",len(failedTests))
        [ print(x) for x in failedTests ]


    def testTwoParametersCombinations(self,parameterName1,parameterName2):

        self.startTestLog()
        
        parameter1Values = self.parametersRanges[parameterName1]
        parameter2Values = self.parametersRanges[parameterName2]
        
        failedTests = []
        
        for parameter1Value in parameter1Values:
            for parameter2Value in parameter2Values:
                
                caseParameters = self.baseCaseParameters.copy()               
                caseParameters[parameterName1] = parameter1Value
                caseParameters[parameterName2] = parameter2Value
        
                try:
                    print("Testing ",caseParameters)
                    caseConfigurator(self.templatesDir,self.buildingsDir).configureSimulation(caseParameters,'test.prj')
                    os.remove('test.prj')

                except:
                    
                    print("Test failed for parameter set ",caseParameters)
                    failedTests.append(caseParameters)

        self.stopTestLog()

        #console print    
        print("Number of failed tests",len(failedTests))
        [ print(x) for x in failedTests ]
        


if __name__ == "__main__":

    templatesDir = os.path.join(dirPath,'..','comisventData','0-TemplatesAndLibs')
    dimBuildingsDir = os.path.join(dirPath,'..','comisventData','2-DimBuildings')

   
    #check that one by one variaton of all parameters works
    ClassConfiguratorTester('singleVar.log',templatesDir,dimBuildingsDir).testSingleParameterVariations()

    # testing compbination of buildings and systems, that are strongly dependent and may reveal issues
    ClassConfiguratorTester('SystemAndBuilding.log',templatesDir,dimBuildingsDir).testTwoParametersCombinations('building','system')



    
    #parameters={'building': 'COVL-REN-HO1', 'orientation': 35, 'v50': 6, 'system': 'Windows', 'control': 'fulllocal', 'occupancy': 'default-active'}
    #caseConfigurator().configureSimulation(parameters,'test.prj')

    
    
    """parameters={'building':'COVL-REN-HO2',
                'orientation':35,
                'v50':6,
                'system':'CNBNSLAAP',
                'control':'fulllocal',
                'occupancy':'default-active'
                }
    

    caseConfigurator(templatesDir,dimBuildingsDir).configureSimulation(parameters,'test.prj')
    """
    

