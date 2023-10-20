import wsm

def apply(contam_data,weatherRoughness,terrainRoughness):
    
    
    flowpaths=contam_data['flowpaths']

    numberOfLevels = contam_data['zones'].getNumberOfLevelsWithzones()

    wsmValue=wsm.wsm(numberOfLevels*3,weatherRoughness,terrainRoughness)

    for index in flowpaths.df.index:
            
        if (flowpaths.df.loc[index,'pw']>0):
            
            flowpaths.df.loc[index,'wPmod']=wsmValue

    
    
    return
