
import contam_objects_new
import os

def apply(contam_data,profileName,templatesFolder):
    
    
    libraryProfiles = readFromLibrary(templatesFolder)

    existing_windPressureProfiles = contam_data['windprofiles']
    existing_windPressureProfiles.replaceFromLibrary(libraryProfiles.df)

    roofProfileID,wallProfileID = getProfilesNumbersFromProfileName(libraryProfiles.df,profileName)

    applyWindPressureProfilesToModel(contam_data,wallProfileID,roofProfileID)

    
    return


def applyWindPressureProfilesToModel(contam_data,wallProfileID,roofProfileID):
    
    flowpaths=contam_data['flowpaths']
    
    #flowelems=contam_data['flowelems']
    #crackelemid=flowelems.df[flowelems.df['name']=='Gen_crack'].index[0]

    for index in flowpaths.df.index:
        
            #by doing so, the ones that would be 0 remain 0
            
        if (flowpaths.df.loc[index,'pw']>0):
            
            flowpaths.df.loc[index,'pw'] = wallProfileID





    

def getProfilesNumbersFromProfileName(profiledf,profileName):
    
    if profileName == 'exposed':
        
        roofProfileID = profiledf[profiledf['name'] ==  'A2.1-Roof>30°' ].index[0]
        wallProfileID = profiledf[profiledf['name'] ==  'A2.1-Walls' ].index[0]

    
    elif profileName == 'semi-exposed':
        
        roofProfileID = profiledf[profiledf['name'] ==  'A2.2-Roof>30°' ].index[0]
        wallProfileID = profiledf[profiledf['name'] ==  'A2.2-Walls' ].index[0]


    elif profileName == 'shielded':
        
        roofProfileID = profiledf[profiledf['name'] ==  'A2.3-Roof>30°' ].index[0]
        wallProfileID = profiledf[profiledf['name'] ==  'A2.3-Walls' ].index[0]


    else:
        print ("Error ",profileName," is not a valid entry")
        
        return None,None

    return roofProfileID,wallProfileID

    
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