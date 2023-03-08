# -*- coding: utf-8 -*-
"""
Created on Tue Oct 12 14:37:35 2021

@author: spec
"""

def scalePlan(*,volumeFactor=1.0,mode='uniform',contam_model=None):
    
    acceptableModes=['uniform','horizontalOnly','verticalOnly']
    
    if (mode not in acceptableModes):
        return


    zones=contam_model['zones']
    flowpaths=contam_model['flowpaths']
    flowelems=contam_model['flowelems']
    crackelemid=flowelems.df[flowelems.df['name']=='Gen_crack'].index[0]



    zonesdf = zones.getZonesDataFrame()
    zonesdf['Vol']=zonesdf['Vol']*volumeFactor

    
    if mode=='uniform':
        
        linearFactor = volumeFactor**(1/3)
        surfaceFactor = linearFactor**2
        

        for index in flowpaths.df.index:
            if (flowpaths.df.loc[index,'pe']==crackelemid):
                flowpaths.df.loc[index,'mult']*= surfaceFactor


    if mode=='horizontalOnly':
        
        wallFacesFactor = volumeFactor**(1/4)
        
        floorAndRoofFactor = volumeFactor**(2/4)
        
        for index in flowpaths.df.index:
            
            if (flowpaths.df.loc[index,'pe']==crackelemid):
            
                if flowpaths.df.loc[index,'dir'] in [1,2,4,5]:
                    flowpaths.df.loc[index,'mult']*= wallFacesFactor

                if flowpaths.df.loc[index,'dir'] in [3,6]:
                    flowpaths.df.loc[index,'mult']*= floorAndRoofFactor



    if mode=='verticalOnly':
        
        wallFacesFactor = volumeFactor
        
        for index in flowpaths.df.index:
            
            if (flowpaths.df.loc[index,'pe']==crackelemid):
            
                if flowpaths.df.loc[index,'dir'] in [1,2,4,5]:
                    flowpaths.df.loc[index,'mult']*= wallFacesFactor





        
    
    return contam_model