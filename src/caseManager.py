import os
import sys
import importlib
import subprocess
import json

dirPath = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.join(dirPath,'contamFunctions'))
sys.path.append(os.path.join(dirPath,'computeFunctions/filters'))
sys.path.append(os.path.join(dirPath,'setFunctions'))
sys.path.append(os.path.join(dirPath,'tools'))
sys.path.append(os.path.join(dirPath,'utilities'))



import contam_functions
import setSystem,setControls,setOccupancyAndSources,setBCS,setWeather,setNumericalParameters,setFilters,setContaminants,setWindPressureProfile,setWindSpeedMultiplier,scalePlan,setLeaks,setOpenstairs
import computeFilters


class caseConfigurator:

    
    def __init__(self,dimBuildingsDir,occupancyDir,weatherDir,libraryDir,contaminantsDir,systemsDir=None,controlsDir=None):
       
        self.defaultParameters={'building':'',
                                'simulationType':'transient',
                                'buildingDimensionsVariation':{
                                    'volumeRatio': 1.0,
                                    'mode': 'uniform'
                                    },
                                'orientation':0,
                                'airTightness':
                                    {'v50':3,
                                     'leaksDistribution':'uniform'},
                                'system':None,
                                'control':None,
                                'occupancy': None,
                                'weather':'',
                                'contaminants':{},
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
        self.systemsDir = systemsDir
        self.controlsDir = controlsDir
    
        self.ContamModel = None

        self.full     = None


    def applyParameters(self):

        self.getBuildingModel()
        self.modifyBuildingDimensions()

        self.setAirtightnessOrientation()

        if self.actualParameters['simulationType']=='blowerDoor':
            self.setBlowerDoor()
            return


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


        self.setOccupancyAndSources()
        self.setExtraContaminants()

        self.setContaminantsFile()  

        
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
        
        if parametersDict['simulationType']=='blowerDoor':

            minimalParameters = ['building','airTightness','outputFiles']        
            
        else:
            
            minimalParameters = ['building','system','weather',
                                 'simulationTimeStep','StartDate','EndDate'
                                 ,'outputTimeStep','outputFiles']        

            
        
        for p in minimalParameters:
            if p not in parametersDict.keys():
                print("Parameter ",p," is required")
                print("Here is the full list of required parameters")
                [print('    '+x) for x in minimalParameters]
                print("")
                raise ValueError("Missing parameters, see above")
    
            
            
            


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
        
        
        buildingFile = os.path.join(self.dimBuildingsDir,self.actualParameters['building']+'.prj')
        if not os.path.exists(buildingFile):
            raise ValueError("ERROR with the building file: "+buildingFile+" does not exist")
    
        
        if self.actualParameters['simulationType'] == 'blowerDoor':
            return
    
        weatherFile = os.path.join(self.weatherDir,self.actualParameters['weather']+'.wth')
        if not os.path.exists(weatherFile):
            raise ValueError("ERROR with the weather file: "+weatherFile+" does not exist")
        
     
        if self.actualParameters['contaminantsFile'] is not None:
            contaminantsFile = os.path.join(self.contaminantsDir,self.actualParameters['contaminantsFile']+'.CTM')
            if not os.path.exists(contaminantsFile):
                raise ValueError("ERROR with the contaminants file: "+contaminantsFile+" does not exist")
        
     
        
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
    

    def setBlowerDoor(self):
        
        self.ContamModel['siminputs'].airFlowsParameters[0] = 4
        self.ContamModel['siminputs'].massFractionParameters[0] = 0
        
        return
        

    def getExtraContaminants(self):
        
        if (self.actualParameters['contaminants'] != None):
            return list(self.actualParameters['contaminants'].keys())
        else:
            return []

    
    def getLeaksInformations(self):

        zones = self.ContamModel['zones'].df
        
        flowelems = self.ContamModel['flowelems'].df
        flowpaths = self.ContamModel['flowpaths'].df

        leakElemIds = flowelems[flowelems['name'].str.contains('_crack')].index

        leaks = flowpaths[flowpaths['pe'].isin(leakElemIds)]
        
        for li in leaks.index:
            
            #leaks.loc[li,'from'] = zones.loc[leaks.loc[li,'pzn']]
            leaks.loc[li,'from']= 'Ext'
            leaks.loc[li,'to'] = zones.loc[leaks.loc[li,'pzm'],'name']
            leaks.loc[li,'v50*area'] = leaks.loc[li,'mult']

        leaks = leaks.filter(items=['from','to','v50*area'])        
        
        leaks.loc['Total','v50*area']=leaks['v50*area'].sum()
        
        return leaks
    


    def getBuildingModel(self):
        
        self.baseFileName = os.path.join(self.dimBuildingsDir,self.actualParameters['building']+'.prj')
        self.ContamModel = contam_functions.loadcontamfile(self.baseFileName)

        self.ContamModel['zones'].defineZonesFunctions(kitchenKey='Keuken',
                                                       laundryKey='Wasplaats',
                                                       bedroomsKey='Slaap',
                                                       bathroomKey='Badkamer',
                                                       toiletKey='WC',
                                                       livingKey='Woonkamer')
        

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

            userArguments=None
            
            if 'arguments' in self.actualParameters['system'].keys():
                userArguments=self.actualParameters['system']['arguments']
        
            systemJSON = self.computeSystem(systemName,userArguments)

        
        elif systemdefinition =='JSONfile':

            systemJSONFile = self.actualParameters['system']['filename']
            with open(systemJSONFile, 'r') as inputFile:
                systemJSON = json.load(inputFile)
            
        else:
            raise ValueError ("Valide system definitions are 'namedSystem' or 'JSONfile'")
            
            
        return systemJSON
        

    def computeSystem(self,systemName,userArguments=None):
        
        if self.systemsDir==None:
            print("No directory for namedSystems")
            raise ValueError("If you use a named system, you should define the location of the named system directory")

        #system=self.actualParameters['system']

        systemComputeFunction,systemArgs = existingSystems(self.systemsDir).functionAndArguments(systemName)

        if userArguments is not None:
            systemArgs = userArguments

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
        
        controlDict=self.actualParameters['control']


        if controlDict == None:

            return systemJson
        
        else:

            controlStrategy = controlDict['controlType']

            if controlStrategy=='constant' or controlStrategy=='systemJSONFile':

                return systemJson

            elif controlStrategy=='namedControlStrategy':        
                

                if self.controlsDir == None:
                    raise ValueError("There is no directory defined for custom control algorithms")

                strategyName = controlDict['controlStrategyName']
        
                computeFunction,optionsDict = existingControls(self.controlsDir).functionAndArguments(strategyName)
                
                kwargs = {}
                kwargs['systemJson']=systemJson
        
            
                if "defaultArguments" in optionsDict.keys():
                    kwargs.update(optionsDict["defaultArguments"])
            
        
                #//allArguments = [systemJson] + extraArguments
                
                if self.actualParameters['system']['definition']=='namedSystem':
                
                    systemName = self.actualParameters['system']['name']

                    if "systemSpecificArguments" in optionsDict.keys():                
                        if systemName in optionsDict["systemSpecificArguments"].keys():
                            kwargs.update(optionsDict["systemSpecificArguments"][systemName])   
        
                if 'extraArguments' in self.actualParameters['control']:
                    kwargs.update(self.actualParameters['control']['extraArguments'])
                    
        
                controlJson = computeFunction(**kwargs)
        
                return controlJson

            else:
                raise ValueError("Uknown control strategy "+controlStrategy)

    def setControls(self,controlJson):
        
        setControls.setControls(self.ContamModel,controlJson)


    def setOccupancyAndSources(self):

        occupancy = self.actualParameters['occupancy']

        if occupancy is not None:
        
            setOccupancyAndSources.apply(self.ContamModel,occupancy,self.occupancyProfilesDir)
        

    def setAirtightnessOrientation(self):
        
        if 'v50' in self.actualParameters['airTightness'].keys():
            leakValue = self.actualParameters['airTightness']['v50']
            leakDefinition = 'v50'
        
        
        elif 'n50' in self.actualParameters['airTightness'].keys():
            leakValue = self.actualParameters['airTightness']['n50']
            leakDefinition = 'n50'
        
        
        #v50= self.actualParameters['v50']
        orientation = self.actualParameters['orientation']
        leaksDistribution = self.actualParameters['airTightness']['leaksDistribution']
        
        setBCS.apply(self.ContamModel,leakDefinition,leakValue,orientation,leaksDistribution)
        
    
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
        
      
    def addFlowSensors(self,transferOpening=True,cracks=True):
        
        from utilityFunctions import shortenTooLongName
        
        zones = self.ContamModel['zones']
        flowelems = self.ContamModel['flowelems']
        flowpaths = self.ContamModel['flowpaths']
        controls = self.ContamModel['controls']


        slopedcrackid = flowelems.df[flowelems.df['name']=='SlopedR_crack'].index[0]
        floorcrackid = flowelems.df[flowelems.df['name']=='Floor_crack'].index[0]
        wallcrackid = flowelems.df[flowelems.df['name']=='Wall_crack'].index[0]
        flatroofcrackid = flowelems.df[flowelems.df['name']=='FlatR_crack'].index[0]

        natTransfers = list(flowelems.df[flowelems.df['name'].str[0:2]=='NT'].index)
        

        print(natTransfers)

        for index in flowpaths.df.index:


            if flowpaths.df.loc[index,'pe'] in natTransfers:

                fromZid = flowpaths.df.loc[index,'pzm'] 
                toZid =   flowpaths.df.loc[index,'pzn'] 
                
                print(fromZid,toZid)
    
                fromZname = zones.df.loc[fromZid,'name']
                toZname = zones.df.loc[toZid,'name']
                 
                shortFromZ = shortenTooLongName(fromZname,4)
                shortToZ = shortenTooLongName(toZname,4)
                
                controls.addflowsensor(index,'Q_TR_'+shortFromZ+'_'+shortToZ)
                
        

    def setExtraContaminants(self):
        
        contaminantsDict = self.actualParameters['contaminants']

        for cName,cDict in contaminantsDict.items():
            
            if 'molarMass' not in cDict.keys():
                cDict['molarMass']=0
            
            self.addContaminant(cName,cDict['outsideConcentration'],cDict['initialConcentration'],cDict['unit'],cDict['molarMass'])

            if 'source' in cDict.keys():
                
                sourceDict = cDict['source']
                
                if sourceDict['type'] == "constantRatePerFloorArea":
                    
                    setOccupancyAndSources.addPollutantSourcePerFloorArea(self.ContamModel,cName,sourceDict['rate'],sourceDict['unit'])

                elif sourceDict['type'] == "constantRatePerTotalArea":
                    
                    setOccupancyAndSources.addPollutantSourcePerTotalArea(self.ContamModel,cName,sourceDict['rate'],sourceDict['unit'])

                else:
                    raise ValueError("Uknown type of source. Possible sources are 'constantRatePerFloorArea' or 'constantRatePerTotalArea'")

        

    def addContaminant(self,name,defaultOutsideConcentration,insideInitialConcentration,unit,MM):

        self.ContamModel['contaminants'].addSpecie(name,defaultOutsideConcentration,unit,MM)
        self.ContamModel['initConc'].addInitConcentration(name,insideInitialConcentration,unit,MM)
        self.addContaminantSensors(name)
        self.addContaminantExposure(name)
        
        



    def addContaminantSensors(self,contaminantName):

        zones = self.ContamModel['zones']
        controls = self.ContamModel['controls']
        
        contaminantUnit = self.ContamModel['contaminants'].getUnitName(contaminantName)
        multiplier = self.ContamModel['contaminants'].kgkgToUnit(contaminantUnit)
        
        
        for zoneid in zones.df.index:
            if ('AHS' not in zones.df.loc[zoneid,'name']):

                controls.addspeciesensor(zones.df,zoneid,contaminantName,contaminantName+'-sensor',multiplier=multiplier,unit=contaminantUnit) #add sensor and report directly

        controls.addspeciesensor(zones.df,-1,contaminantName,contaminantName+'-sensor',multiplier=multiplier,unit=contaminantUnit) # for EXT 
        
  
    def addContaminantExposure(self,contaminantName):


        occupants = self.ContamModel['exposures']
        controls = self.ContamModel['controls']

        contaminantUnit = self.ContamModel['contaminants'].getUnitName(contaminantName)
        multiplier = self.ContamModel['contaminants'].kgkgToUnit(contaminantUnit)


        for oid in range(1,occupants.nexposures+1):

            print(contaminantName)
            controls.addexposuresensor(oid,contaminantName,description=contaminantName+'-'+str(oid),multiplier=multiplier)



    def setLeaks(self):
        
        if self.actualParameters['internalLeaks']:
            
            setLeaks.apply(self.ContamModel)


    def setOpenStairs(self):
        
        if self.actualParameters['openStairs']:
            setOpenstairs.apply(self.ContamModel)




class contamRunner:
    
        def __init__(self,contamExeDir):
            self.contamExe = os.path.join(contamExeDir,'contamx34.exe')
    
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


            
            print("CONTAM run terminated")


        def makePrjRelative(self,prjFile):
            
            workingDir = os.getcwd()
            
            prefixToRemove = os.path.commonpath([workingDir,prjFile])
            
            prjFileRelative = prjFile.replace(prefixToRemove,'')

            return prjFileRelative





class existingSystems:
    
    def __init__(self,systemRulesDirectory):
        
        sys.path.append(systemRulesDirectory)
        
        file= os.path.join(systemRulesDirectory,"namedSystems.json")
        
        f = open(file)
        self.systems=json.load(f)
        f.close()
        

        
    def functionAndArguments(self,system):
                       
        if (system not in self.getExistingSystems()):
            raise ValueError("System "+system+" does not exist in the list of named systems")
        
        systemModule = importlib.import_module(self.systems[system]['file'])        
        
        return systemModule.compute,self.systems[system]['arguments']


    def getExistingSystems(self):
        
        return list(self.systems.keys())



class existingControls:
    
    def __init__(self,controlsDirectory):
        
        sys.path.append(controlsDirectory)
        
        file= os.path.join(controlsDirectory,"namedControls.json")
        
        f = open(file,'r')
        self.controlsDict=json.load(f)
        f.close()

        
    def functionAndArguments(self,controlName):
        
                       
        controlModule = importlib.import_module(self.controlsDict[controlName]['file'])        
        
        
        return controlModule.compute,self.controlsDict[controlName]


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
























    

