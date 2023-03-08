import wsm

def apply(contam_data,weatherRoughness,terrainRoughness):
    
    
    flowpaths=contam_data['flowpaths']

    wsmValue=wsm.wsm(6,weatherRoughness,terrainRoughness)

    for index in flowpaths.df.index:
            
        if (flowpaths.df.loc[index,'pw']>0):
            
            flowpaths.df.loc[index,'wPmod']=wsmValue

    
    
    return
