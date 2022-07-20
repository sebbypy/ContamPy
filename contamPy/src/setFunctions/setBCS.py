

def apply(contam_data,v50,rot,leaks_distrib='uniform'):


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



    if leaks_distrib == 'walls':

        totalArea = 0.
        wallArea = 0.
        for index in flowpaths.df.index:
            
            if (flowpaths.df.loc[index,'pe']==crackelemid):
                totalArea += flowpaths.df.loc[index,'mult']
    
                if flowpaths.df.loc[index,'dir'] not in [3,6]: #3 and 6 are vertical paths
                    wallArea += flowpaths.df.loc[index,'mult']
                
        correctedv50 = v50*totalArea/wallArea
                
        
    else:
        correctedv50 = v50

            

    """
    These values have been check on HO1 model, they are 100% consisten with the excel
    print("Total area",totalArea)
    print("Wall area",wallArea)
    """
    
    for index in flowpaths.df.index:
        
        if (flowpaths.df.loc[index,'pe']==crackelemid):

            if leaks_distrib == 'walls':

                if flowpaths.df.loc[index,'dir'] not in [3,6]: #3 and 6 are vertical paths
                    
                    flowpaths.df.loc[index,'mult']*=float(correctedv50) 
                
    
            else: #normal case:
                
                flowpaths.df.loc[index,'mult']*=float(correctedv50) 
       
                
       
        #by doing so, the ones that would be 0 remain 0
            
        if (flowpaths.df.loc[index,'pw']>0):
            
            flowpaths.df.loc[index,'wazm']+=int(rot)
            #flowpaths.df.loc[index,'wPmod']=wsmValue


