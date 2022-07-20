
import contam_objects_new
import os

def apply(contam_data,profileName,templatesFolder):
    
    
    libraryProfiles = readFromLibrary(templatesFolder)

    #get the right IDS from the library file
    roofProfileID,wallProfileID,flatProfileID = getProfilesNumbersFromProfileName(libraryProfiles.df,profileName)

    #apply the profiles ID from the library data to the flow paths
    applyWindPressureProfilesToModel(contam_data,wallProfileID,roofProfileID,flatProfileID)


    # replace the existing profile by the library profiles
    existing_windPressureProfiles = contam_data['windprofiles']
    existing_windPressureProfiles.replaceFromLibrary(libraryProfiles.df) #when I do that I change the numbering



    
    return


def applyWindPressureProfilesToModel(contam_data,wallProfileID,roofProfileID,flatProfileID):
    
    flowpaths=contam_data['flowpaths']
    wprofiles = contam_data['windprofiles']
    
    #print(wprofiles.df)
    
    #print(flowpaths.df.to_string())
    #flowelems=contam_data['flowelems']
    #crackelemid=flowelems.df[flowelems.df['name']=='Gen_crack'].index[0]

    for index in flowpaths.df.index:
        
        #by doing so, the ones that would be 0 remain 0
            
        if (flowpaths.df.loc[index,'pw']>0):
            
            currentProfileID = flowpaths.df.loc[index,'pw']          
            currentProfile = wprofiles.df.loc[currentProfileID,'name']
            
            
            if ('Wall') in currentProfile:
                flowpaths.df.loc[index,'pw'] = wallProfileID
            elif ('Flat') in currentProfile:
                flowpaths.df.loc[index,'pw'] = flatProfileID
            elif ('30') in currentProfile:
                flowpaths.df.loc[index,'pw'] = roofProfileID
            else:
                print("ERROR with wind profiles")
                
                

                                   
            



    

def getProfilesNumbersFromProfileName(profiledf,profileName):
    
    if profileName == 'exposed':
        
        roofProfileID = profiledf[profiledf['name'] ==  'A2.1-Roof>30°' ].index[0]
        wallProfileID = profiledf[profiledf['name'] ==  'A2.1-Walls' ].index[0]
        flatProfileID = profiledf[profiledf['name'] ==  'A2.1-FlatRoof' ].index[0]


    
    elif profileName == 'semi-exposed':
        
        roofProfileID = profiledf[profiledf['name'] ==  'A2.2-Roof>30°' ].index[0]
        wallProfileID = profiledf[profiledf['name'] ==  'A2.2-Walls' ].index[0]
        flatProfileID = profiledf[profiledf['name'] ==  'A2.2-FlatRoof' ].index[0]


    elif profileName == 'shielded':
        
        roofProfileID = profiledf[profiledf['name'] ==  'A2.3-Roof>30°' ].index[0]
        wallProfileID = profiledf[profiledf['name'] ==  'A2.3-Walls' ].index[0]
        flatProfileID = profiledf[profiledf['name'] ==  'A2.3-FlatRoof' ].index[0]


    else:
        print ("Error ",profileName," is not a valid entry")
        
        return None,None

    return roofProfileID,wallProfileID,flatProfileID

    
def readFromLibrary(templatesFolder):
    
    libraryFile = os.path.join(templatesFolder,'WindProfiles.lb2')   
    
    f=open(libraryFile,'r',errors='ignore')
    line=True
    while(line):
        line = f.readline()
        if ('wind pressure profiles' in line):
            wp=contam_objects_new.windpressureprofiles()
            wp.read(f,line)


    return wp