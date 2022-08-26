import numpy as np

def apply(contam_data,v50,rot,leaks_distrib='uniform'):


    flowpaths=contam_data['flowpaths']
    flowelems=contam_data['flowelems']

    crackElementsIds={}

    for cracktype in ['Floor_crack','Wall_crack','FlatR_crack','SlopedR_crack']:
                        
        if cracktype in flowelems.df['name'].values:
            
            crackElementsIds[cracktype] = flowelems.df[flowelems.df['name']==cracktype].index[0]

        else:
            
            crackElementsIds[cracktype] = np.nan


    if leaks_distrib=='random':
        
        leakpaths = flowpaths.df[flowpaths.df['pe'].isin(crackElementsIds.values())]
        
        nleaks = len(leakpaths)
        
        randomNumbers = np.random.uniform(0,1,size=nleaks)
        
        randomSum = randomNumbers.sum()
        
        correctionFactor = getTotalArea(flowpaths,crackElementsIds)/randomSum
        
        leakAreas = randomNumbers*correctionFactor

        
        for index,area in zip(leakpaths.index,leakAreas):        
        
            flowpaths.df.loc[index,'mult'] = area
            
        return


    if leaks_distrib == 'walls':

        totalArea = getTotalArea(flowpaths,crackElementsIds)
        wallArea = getWallArea(flowpaths,crackElementsIds)                
        correctedv50 = v50*totalArea/wallArea       


    else:
        correctedv50 = v50


    for index in flowpaths.df.index:
        
        
        if (flowpaths.df.loc[index,'pe']==crackElementsIds['Wall_crack']):
                    
            flowpaths.df.loc[index,'mult']*=float(correctedv50) 
    
        else: #normal case:
                
            flowpaths.df.loc[index,'mult']*=float(correctedv50) 
       

        #by doing so, the ones that would be 0 remain 0           
        if (flowpaths.df.loc[index,'pw']>0):
            
            flowpaths.df.loc[index,'wazm']+=int(rot)
            #flowpaths.df.loc[index,'wPmod']=wsmValue



def getTotalArea(flowpaths,crackElementsIds):

    totalArea=0    

    for index in flowpaths.df.index:
        
        if flowpaths.df.loc[index,'pe'] in crackElementsIds.values():

            totalArea += flowpaths.df.loc[index,'mult']
    
    return totalArea


def getWallArea(flowpaths,crackElementsIds):

    wallArea=0
    
    for index in flowpaths.df.index:
        
        if flowpaths.df.loc[index,'pe'] == crackElementsIds['Wall_crack'] : 
            
            wallArea += flowpaths.df.loc[index,'mult']

    return wallArea


def getFloorArea(flowpaths,crackElementsIds):

    floorArea=0
    
    for index in flowpaths.df.index:
        
        if flowpaths.df.loc[index,'pe'] == crackElementsIds['Floor_crack'] : 
            
            floorArea += flowpaths.df.loc[index,'mult']

    return floorArea

