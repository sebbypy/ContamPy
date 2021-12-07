

def apply(contam_data,v50,rot):


    # Usage
    # python apply_system contam_file.prj  system_file.csv output.prj

    # ----------------------------------
    # Load CONTAM FILE and various parts
    # ----------------------------------

    flowpaths=contam_data['flowpaths']
    flowelems=contam_data['flowelems']


    crackelemid=flowelems.df[flowelems.df['name']=='Gen_crack'].index[0]

    #Winds speed multiplier
    # Defaults parameters for now
    #def wsm(building_height,building_terrain_category,meteo_terrain_category):

    """print("hello, world")
    print(roughnessWeatherStation,roughnessBuilding)

    wsmValue=wsm.wsm(6,'II','II')
    """
    for index in flowpaths.df.index:
        
        if (flowpaths.df.loc[index,'pe']==crackelemid):
    
            flowpaths.df.loc[index,'mult']*=float(v50) 
            #by doing so, the ones that would be 0 remain 0
            
        if (flowpaths.df.loc[index,'pw']>0):
            
            flowpaths.df.loc[index,'wazm']+=int(rot)
            #flowpaths.df.loc[index,'wPmod']=wsmValue


