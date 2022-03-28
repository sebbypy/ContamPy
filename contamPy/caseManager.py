import os
import sys
import importlib
import subprocess
import json

dirPath = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.join(dirPath,'contamFunctions'))
sys.path.append(os.path.join(dirPath,'computeFunctions/systems'))
sys.path.append(os.path.join(dirPath,'computeFunctions/controls'))
sys.path.append(os.path.join(dirPath,'computeFunctions/filters'))
sys.path.append(os.path.join(dirPath,'setFunctions'))
sys.path.append(os.path.join(dirPath,'tools'))



import contam_functions
import setSystem,setControls,setOccupancyAndSources,setBCS,setWeather,setNumericalParameters,setFilters,setContaminants,setWindPressureProfile,setWindSpeedMultiplier,scalePlan,setLeaks,setOpenstairs
import computeControls,computeFilters,computeOpenDoors


class caseConfigurator:

    
    def __init__(self,dimBuildingsDir,occupancyDir,weatherDir,libraryDir,contaminantsDir):
       
        self.defaultParameters={'building':'COVL-REN-HO1',
                                'buildingDimensionsVariation':{
                                    'volumeRatio': 1.0,
                                    'mode': 'uniform'
                                    },
                                'orientation':0,
                                'v50':3,
                                'system':{
                                        'definition':'namedSystem',
                                        'name':'DPREVENT'
                                        },
                                'control':'constant',
                                'occupancy':'default-home',
                                'weather':'Uccle',
                                'extraContaminants':{},
                                'filters':None,
                                'contaminantsFile':None,
                                'shielding':'semi-exposed',
                                'terrainRoughness':'II',
                                'weatherRoughness':'II',
                                'simulationTimeStep':'00:05:00',
                                'StartDate':'Mar01',
                                'EndDate':'Mar03',
                                'outputTimeStep':'00:05:00',
                                'outputFiles':['simflow','simconc','log','ach'],
                                'openDoors':False,
                                'internalLeaks':False,
                                'openStairs':False
                                }
        
        self.actualParameters=self.defaultParameters.copy()

        self.dimBuildingsDir = dimBuildingsDir
        self.occupancyProfilesDir = occupancyDir
        self.weatherDir = weatherDir
        self.contaminantsDir = contaminantsDir
        self.libraryDir = libraryDir        
    
        self.ContamModel = None

        self.full     = None


    def applyParameters(self):

        self.getBuildingModel()
        self.modifyBuildingDimensions()

        self.setNumericalParameters()

        systemJSON = self.getSystemJson()
        #systemJSON = self.computeSystem()               
        self.setSystem(systemJSON)

        self.setLeaks()
        self.setOpenStairs()
        
        controlJSON = self.computeControl(systemJSON)     
        self.setControls(controlJSON)

        filterJSON = self.computeFilters(controlJSON)
        self.setFilters(filterJSON)

        self.fullJSON = filterJSON

        self.setExtraContaminants()

        self.setOccupancyAndSources()

        self.setContaminantsFile()  

        self.setAirtightnessOrientation()
        
        self.setWeather()
        
        self.setShielding()
        
        self.setWSM()

        

    def configureSimulation(self,outputFileName,parametersDict,numericalParameters=None):
        
        self.setAllPhysicalParameters()

        if (numericalParameters != None):
            self.setNumericalParameters(numericalParameters)
            
        self.writeContamFile(outputFileName)


    def setAllPhysicalParameters(self):

        self.getBuildingModel()

        systemJSON = self.computeSystem()        
        self.setSystem(systemJSON)
        
        controlJSON = self.computeControl(systemJSON)     
        self.setControls(controlJSON)
        
        filterJSON = self.computeFilters(controlJSON)
        self.setFilters(filterJSON)

        self.setOccupancyAndSources()

        self.setAirtightnessOrientation()
        self.setWeather()
    
    
    def setSystemFromParameters(self):
        
        systemJSON = self.computeSystem()        
        self.setSystem(systemJSON)
        
        controlJSON = self.computeControl(systemJSON)     
        self.setControls(controlJSON)

        filterJSON = self.computeFilters(controlJSON)
        self.setFilters(filterJSON)

        self.fullJSON = filterJSON
        

    
    def setBoundaryParameters(self):
        
        self.setWeather()
        self.setContaminantsFile()
        self.setShielding()
        self.setWSM()



    def setSystemFromJSON(self,systemJSONFile):
        
          
        with open(systemJSONFile, 'r') as inputFile:
            systemJSON = json.load(inputFile)
        
        self.setSystem(systemJSON)       
        self.setControls(systemJSON)
        self.setFilters(systemJSON)
        


    def setBuildingParameters(self):

        
        self.getBuildingModel()
        self.setAirtightnessOrientation()
        self.setWeather()
        
        

    def readParameters(self,parametersDict):

        
        if (self.doParametersExist(parametersDict)):
            
            for key in parametersDict.keys():
    
                self.actualParameters[key]=parametersDict[key]

            self.areActualParametersValid()
    
    
    
    def doParametersExist(self,parametersDict):
        
        for key in parametersDict.keys():
            
            if key not in self.defaultParameters.keys():
                raise NameError('Unkown parameter '+key)

        return True


    def areActualParametersValid(self):
        
        if self.actualParameters['control']=='file' and self.actualParameters['system']!='file':
            raise ValueError("Control cannot be defined in a file if the system also is")
            
        if self.actualParameters['filters']=='file' and self.actualParameters['system']!='file':
            raise ValueError("Filters cannot be defined in a file if the system also is")
            
    
        if self.actualParameters['filters'] != None:
            
            defaultSpecies = ['CO2','H2O','VOC']
            
            allSpecies = defaultSpecies+self.getExtraContaminants();
                        
            
            for filterSpecie in self.actualParameters['filters'].keys():
                
                if (filterSpecie not in allSpecies):
                    raise ValueError("A filter cannot be defined for contaminant "+filterSpecie+".The existing contaminants are "+str(allSpecies))
    

    def getExtraContaminants(self):
        
        if (self.actualParameters['extraContaminants'] != None):
            return list(self.actualParameters['extraContaminants'].keys())
        else:
            return []

    

    def getBuildingModel(self):
        
        self.baseFileName = os.path.join(self.dimBuildingsDir,self.actualParameters['building']+'.prj')
        self.ContamModel = contam_functions.loadcontamfile(self.baseFileName)


    def modifyBuildingDimensions(self):
        
        modifierDict = self.actualParameters['buildingDimensionsVariation']
        volumeFactor = modifierDict['volumeRatio']
        mode = modifierDict['mode']
        
        self.ContamModel = scalePlan.scalePlan(volumeFactor=volumeFactor,mode=mode,contam_model=self.ContamModel)


    def writeContamFile(self,outputFileName):
        
        #def writecontamfile(reffile,newname,datadict):
        finalFileName = os.path.join(os.getcwd(),outputFileName)
       
        contam_functions.writecontamfile(self.baseFileName,finalFileName,self.ContamModel)

    def writeCurrentJSON(self,jsonFileName):
       
        with open(jsonFileName, 'w') as outfile:
            json.dump(self.fullJSON, outfile,indent=2)

        
        

    def getSystemJson(self):

        systemdefinition = self.actualParameters['system']['definition']
        
        if systemdefinition == 'namedSystem':
         
            systemName = self.actualParameters['system']['name']
            systemJSON = self.computeSystem(systemName)
        
        
        elif systemdefinition =='file':

            systemJSONFile = self.actualParameters['system']['file']
            with open(systemJSONFile, 'r') as inputFile:
                systemJSON = json.load(inputFile)
            
        else:
            print("Error in getSystem")
            
            
        return systemJSON
        

    def computeSystem(self,systemName):
        
        #system=self.actualParameters['system']

        systemComputeFunction,systemArgs = existingSystems().functionAndArguments(systemName)

        allArguments = [self.ContamModel] + systemArgs

        json = systemComputeFunction(allArguments)

        
        openDoors = self.actualParameters['openDoors']
        
        if (openDoors):
            json = computeOpenDoors.compute(contamModel=self.ContamModel,systemJSON=json)

        return json


    def setSystem(self,systemJson):
        
        setSystem.apply(self.ContamModel,systemJson)
        

    def computeFilters(self,systemJson):
        
        if (self.actualParameters['filters']==None):
            return systemJson
        
        allArguments = [systemJson,self.actualParameters['filters']]

        jsonData = computeFilters.compute(allArguments)


        return jsonData

    def setFilters(self,filterJSON):

        if ("Filters" not in filterJSON.keys()):
            return
        
        setFilters.setFilters(self.ContamModel,filterJSON)
        


    def computeControl(self,systemJson):
        
        controlStrategy=self.actualParameters['control']

        computeFunction,arguments = existingControls().functionAndArguments(controlStrategy)
        
        kwargs = {}
        kwargs['systemJson']=systemJson
        kwargs.update(arguments)
        
        #//allArguments = [systemJson] + extraArguments
        
        if self.actualParameters['system']['definition']=='namedSystem':
        
            if (self.actualParameters['system']['name'][0] == 'D' and controlStrategy == 'fulllocal'):
                #allArguments.append('balanced')
                kwargs['balance']=True
    
            if (self.actualParameters['system']['name'] == 'CPREVENT' and controlStrategy in ['fulllocalRTOsBal','fulllocalBal']):
                #allArguments.append('balanced')
                kwargs['balance']=True


        controlJson = computeFunction(**kwargs)


        return controlJson


    def setControls(self,controlJson):
        
        setControls.setControls(self.ContamModel,controlJson)


    def setOccupancyAndSources(self):

        occupancy = self.actualParameters['occupancy']
        
        setOccupancyAndSources.apply(self.ContamModel,occupancy,self.occupancyProfilesDir)
        

    def setAirtightnessOrientation(self):
        
        v50= self.actualParameters['v50']
        orientation = self.actualParameters['orientation']
        
        setBCS.apply(self.ContamModel,v50,orientation)
        
    
    def setWeather(self):

        weather = self.actualParameters['weather']        
        weatherFile = os.path.join(self.weatherDir,weather+'.wth')

        #
        if (os.name == 'posix'):
            weatherFile = os.path.relpath(weatherFile)
            
        
        setWeather.apply(self.ContamModel,weatherFile)


    def setShielding(self):

        setWindPressureProfile.apply(self.ContamModel,self.actualParameters['shielding'],self.libraryDir)


    def setWSM(self):
        
        setWindSpeedMultiplier.apply(self.ContamModel,self.actualParameters['weatherRoughness'],self.actualParameters['terrainRoughness'])
        
    
    def setContaminantsFile(self):
        
        contaminants = self.actualParameters['contaminantsFile']        
        
        if (contaminants==None):
            return
        
        contaminantsFile = os.path.join(self.contaminantsDir,contaminants+'.CTM')

        if (os.name == 'posix'):
            contaminantsFile = os.path.relpath(contaminantsFile)
            
        setContaminants.apply(self.ContamModel,contaminantsFile)


    def setNumericalParameters(self):
               
        setNumericalParameters.apply(self.ContamModel,self.actualParameters)


    def writeControlJSON(self,outputFileName):
    
        
        systemJSON = self.computeSystem()        
        controlJSON = self.computeControl(systemJSON)     
        
        with open(outputFileName, 'w') as outfile:
            json.dump(controlJSON, outfile)
        

    def setExtraContaminants(self):
        
        contaminantsDict = self.actualParameters['extraContaminants']

        for cName,cDict in contaminantsDict.items():
            self.addContaminant(cName,cDict['exterior default concentration'],cDict['initial concentration'])
            

    def addContaminant(self,name,defaultOutsideConcentration,insideInitialConcentration):

        self.ContamModel['contaminants'].addSpecie(name,defaultOutsideConcentration)
        self.ContamModel['initConc'].addInitConcentration(name,insideInitialConcentration)
        self.addContaminantSensors(name)
        self.addContaminantExposure(name)


    def addContaminantSensors(self,contaminantName):

        zones = self.ContamModel['zones']
        controls = self.ContamModel['controls']
        
        for zoneid in zones.df.index:
            if ('AHS' not in zones.df.loc[zoneid,'name']):

                controls.addspeciesensor(zones.df,zoneid,contaminantName,contaminantName+'-sensor') #add sensor and report directly


        controls.addspeciesensor(zones.df,-1,contaminantName,contaminantName+'-sensor') # for EXT 
        
  
    def addContaminantExposure(self,contaminantName):

        occupants = self.ContamModel['exposures']
        controls = self.ContamModel['controls']

        for oid in range(1,occupants.nexposures+1):
        
            controls.addexposuresensor(oid,contaminantName,description=contaminantName+'-'+str(oid))



    def setLeaks(self):
        
        if self.actualParameters['internalLeaks']:
            
            setLeaks.apply(self.ContamModel)


    def setOpenStairs(self):
        
        if self.actualParameters['openStairs']:
            setOpenstairs.apply(self.ContamModel)


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
                    'CPREVENT10Pa':{
                            'file':'compute_PREVENT',
                            'arguments':['C','auto-balance-prop','10']
                            },
                    'CCascadePREVENT':{
                            'file':'compute_PREVENT',
                            'arguments':['CRecyclage','auto-balance-prop']
                            },

                    'DPREVENT':{
                            'file':'compute_PREVENT',
                            'arguments':['D','auto-balance-prop']
                            },
                    'DCascadePREVENT':{
                            'file':'compute_PREVENT',
                            'arguments':['DRecyclage','auto-balance-prop']
                            },
                    'CSLAAPPREVENT':{
                            'file':'compute_PREVENT',
                            'arguments':['CSLAAP']
                            },
                    'CSupplyHall':{
                            'file':'compute_PREVENT',
                            'arguments':['CsupplyHall','xx','10']
                            },
                    'Windows':{
                            'file':'compute_SingleSidedWindows',
                            'arguments':[]}                          
                          
                    }
        
    def functionAndArguments(self,system):
                       
        systemModule = importlib.import_module(self.systems[system]['file'])        
        
        return systemModule.compute,self.systems[system]['arguments']


    def getExistingSystems(self):
        
        return list(self.systems.keys())



class existingControls:
    
    def __init__(self):
        
        self.controlsDict={
                    'constant':{
                                'file':'computeControls',
                                'arguments':
                                    {'strategy':'constant','flowFraction':1.0}
                                },
                    'constant70':{
                                'file':'computeControls',
                                'arguments':
                                {'strategy':'constant','flowFraction':0.7}
                                },
                    'constant50':{
                                'file':'computeControls',
                                'arguments':
                                {'strategy':'constant','flowFraction':0.5}
                                },
                    'singleNightClock':{
                                'file':'computeControls',
                                'arguments':
                                {'strategy':'singleClock','schedule':'nightClock','minFlow':0.3,'maxFlow':1.0},
                                },
                    'CentralCO2Living':{
                                'file':'computeControls',
                                'arguments':
                                {'strategy':'CO2Central','minFlow':0.65,'maxFlow':1.0,'balance':True},
                                },
                    'CentralCO2Hall':{
                                'file':'computeControls',
                                'arguments':
                                {'strategy':'CO2CentralHall','minFlow':0.3,'maxFlow':1.0,'balance':True},
                                },

                    'CentralCO2LivingAndNightClock':{
                                'file':'computeControls',
                                'arguments':
                                {'strategy':'NightClockCO2Central','minFlow':0.3,'maxFlow':1.0,'nightFlow':0.7,'balance':True},
                                },
                    'LocalCO2LivingAndNightClock':{
                                'file':'computeControls',
                                'arguments':
                                {'strategy':'NightClockCO2Local','minFlow':0.3,'maxFlow':1.0,'nightFlow':0.7,'balance':True},
                                },
                    'fulllocal':{
                                'file':'computeControls',
                                'arguments':
                                    {'strategy':'fulllocal'}
                                },
                    'fulllocalRTOs':{
                                'file':'computeControls',
                                'arguments':
                                    {'strategy':'fulllocalRTOs'}
                                },
                    'fulllocalRTOsBal':{
                                'file':'computeControls',
                                'arguments':
                                    {'strategy':'fulllocalRTOs','balance':True}
                                },
                    'allMotRTOAndGlobalExtract':{
                            'file':'computeControls',
                            'arguments':
                                {'strategy':'allMotRTOAndGlobalExtract'}
                            },
                    'oneMotRTOAndGlobalExtract':{
                            'file':'computeControls',
                            'arguments':
                                {'strategy':'oneMotRTOAndGlobalExtract'}
                            },
                    
                    'fulllocal30pc':{
                                'file':'computeControls',
                                'arguments':
                                    {
                                    'strategy':'fulllocal',
                                    'minFlow':0.3
                                     }
                                },                          
                          
                    }
        
    def functionAndArguments(self,controlName):
        
                       
        controlModule = importlib.import_module(self.controlsDict[controlName]['file'])        
        
        return controlModule.compute,self.controlsDict[controlName]['arguments']


    def getExistingControls(self):
        
        return list(self.controls.keys())





        

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
                                 list(existingControls().systems.keys()),
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
                    caseConfigurator(self.templatesDir,self.buildingsDir).configureSimulation('test.prj',caseParameters)
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
                    caseConfigurator(self.templatesDir,self.buildingsDir).configureSimulation('test.prj',caseParameters)
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

    
    # Test Single Case
    parameters={'building': 'COVL-REN-HO1', 'orientation': 35, 'v50': 6, 'system': 'Windows', 'control': 'fulllocal', 'occupancy': 'default-active'}
    caseConfigurator(templatesDir,dimBuildingsDir).configureSimulation('test.prj',parameters)

    # Test all variations of a single parameter
    ClassConfiguratorTester('singleVar.log',templatesDir,dimBuildingsDir).testSingleParameterVariations()

    # Test all combinations of building/system since there are strong interactions
    ClassConfiguratorTester('SystemAndBuilding.log',templatesDir,dimBuildingsDir).testTwoParametersCombinations('building','system')
























    

