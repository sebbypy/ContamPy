

#from contam_objects import *
import pandas as pd
import numpy as np
import matplotlib.path as mplPath

import itertools

import contam_objects_new


def loadcontamfile(fname):
    
    f=open(fname,'r',errors='ignore')
    
    #g=open('test','w')
    
    line=True
    while(line):

        line=f.readline()
       
        if ('levels plus icon data' in line):
        
            levels=contam_objects_new.levels()
            levels.readCONTAMlevels(f,line)
            
        if ('zones:' in line):
        
            zones=contam_objects_new.zones()
            zones.readCONTAMzones(f,line)          
                
        if ('flow path' in line):

            flowpaths=contam_objects_new.flowpaths()
            flowpaths.readCONTAMfp(f,line)

        if ('flow elements' in line):
            flowelems=contam_objects_new.flowelements()
            flowelems.readCONTAMflowelements(f,line)
 
        if ('contaminants' in line):
            contaminants=contam_objects_new.contaminants()
            contaminants.read(f,line)
 
        if ('control node' in line):
            controls=contam_objects_new.controlnodes()
            controls.read(f,line)
            
        if ('simple AHS' in line):
            ahs=contam_objects_new.ahs()
            ahs.read(f,line)
            
        if ('wind pressure profiles' in line):
            wp=contam_objects_new.windpressureprofiles()
            wp.read(f,line)
            
            
        if ('occupancy schedules' in line):
            oschedule=contam_objects_new.occupancy_schedules()
            oschedule.read(f,line)

        if ('day-schedules' in line):
            dayschedules=contam_objects_new.daySchedules()
            dayschedules.read(f,line)

        if ('week-schedules' in line):
            weekschedules=contam_objects_new.weekSchedules()
            weekschedules.read(f,line)

        if ('exposures' in line):
            exposures=contam_objects_new.exposures()
            exposures.read(f,line)

        if ('source/sink elements' in line):
            sourceselements=contam_objects_new.sourceElements()
            sourceselements.read(f,line)

        if ('source/sinks:' in line):
            sources=contam_objects_new.sources()
            sources.read(f,line)

        if ('ContamW' in line):
            siminputs=contam_objects_new.SimInputs()
            siminputs.read(f,line)



    datadict={'levels':levels,
            'zones':zones,
            'flowpaths':flowpaths,
            'flowelems':flowelems,
            'contaminants':contaminants,
            'controls':controls,
            'ahs':ahs,
            'windprofiles':wp,
            'oschedules':oschedule,
            'dayschedules':dayschedules,
            'weekschedules':weekschedules,
            'exposures':exposures,
            'sourceelems':sourceselements,
            'sources':sources,
            'siminputs':siminputs
            }
       
    return datadict

def writecontamfile(reffile,newname,datadict):
    
    #datadict is a dictionnary of CONTAM blocks
    # keys: ['levels','zones','flowpaths']
    
    f=open(reffile,'r',errors='ignore')
    g=open(newname,'w')
   
    line=True
    block=False
    while(line):

        line=f.readline()
       
        if ('-999' in line):
            block=False
               
        if ('levels plus icon data' in line):
            block=True
            #levels=contam_objects_new.levels()
            #levels.readCONTAMlevels(f,line)
            datadict['levels'].writeCONTAMlevels(g)
            
        if ('zones:' in line):
            block=True
            #zones=contam_objects_new.zones()
            #zones.readCONTAMzones(f,line)
            datadict['zones'].writeCONTAMzones(g)
               
        if ('flow path' in line):
            block=True
            #flowpaths=contam_objects_new.flowpaths()
            datadict['flowpaths'].writeCONTAMfp(g)
        
        if ('flow elements' in line):
            block=True
            datadict['flowelems'].writeCONTAMflowelements(g)
        
        if ('contaminants' in line):
            block=True
            datadict['contaminants'].write(g)
        
        if ('control node' in line):
            block=True
            datadict['controls'].write(g)

        if ('wind pressure profiles' in line):
            block=True
            datadict['windprofiles'].write(g)
        
        if ('occupancy schedules' in line):
            block=True
            datadict['oschedules'].write(g)

        if ('day-schedules' in line):
            block=True
            datadict['dayschedules'].write(g)
        
        if ('week-schedules' in line):
            block=True
            datadict['weekschedules'].write(g)

        if ('exposures' in line):
            block=True
            datadict['exposures'].write(g)

        if ('source/sink elements' in line):
            block=True
            datadict['sourceelems'].write(g)

        if ('source/sinks:' in line):
            block=True
            datadict['sources'].write(g)
        
        if ('ContamW' in line):
            block=True
            datadict['siminputs'].write(g)

        
        if (block==False):
            g.write(line)


    f.close()
    g.close()
    return 0







def getlevels(fname):

    f=open(fname,'r',errors='ignore')
    line=True

    leveldf=pd.DataFrame()

    while(line):
    
        line=f.readline()
        
        if ('levels plus icon data' in line):

            nlevels=int(line.split()[0])

            
            line=f.readline() #headers
            
            for i in range(nlevels):
                line=f.readline()
                fields=line.split()
                name=fields[6]
                deltaH=float(fields[2])
                refH=float(fields[1])
                levelid=int(fields[0])
                
                leveldf.loc[levelid,'Name']=name
                leveldf.loc[levelid,'refH']=refH
                leveldf.loc[levelid,'deltaH']=deltaH
                
                nicons=int(fields[3])
                
                f.readline() #ico headers

                for ico in range(nicons):
                    f.readline()
            
            f.close()
            return leveldf

def getzones(fname,returntype='list'):

    zones=[]
    f=open(fname,'r',errors='ignore')
    line=True

    zonesdf=pd.DataFrame()

    levelsdf=getlevels(fname)


    while(line):

        line=f.readline()
     
        if ('zones:' in line):
        
            nzones=int(line.split()[0])

            line=f.readline() #header

            for i in range(nzones):
                line=f.readline()
                line=line.split()

                n=int(line[0])
                v=float(line[7])
               
                levelid=int(line[5])
               
                name=line[10].strip()
                
                zones.append(zone(n,v,name))
                zonesdf.loc[n,'Name']=name
                zonesdf.loc[n,'Volume']=v

                zonesdf.loc[n,'Level']=levelsdf.loc[levelid,'Name']

            zones.append(zone(-1,0,'ext'))
            zonesdf.loc[-1,'Volume']=0
            zonesdf.loc[-1,'Name']='ext'

            #zones.append(zone(-1,0,'dummy')) #pour que zones[-2] renvoie vers 'ext'

            f.close()

            if (returntype=='dataframe'):
                return(zonesdf)
            else:
                return zones
        
def getflowelements(fname):
        
    flowelems=[]
    f=open(fname,'r',errors='ignore')
    line=True
       
    while (line):
        line=f.readline()
       
        if ('flow elements' in line):
            nelems=int(line.split()[0])

            for i in range(nelems):

                line=f.readline()
                line=line.split()

                eid=int(line[0])
                icon=line[1]
                elemtype=line[2]
                name=line[-1]

                comment=f.readline()
                comment=comment.replace('\n','')

                data=f.readline()
                #flowelems[name]=flowelement(eid,name,comment)
                #flowelems[eid]=flowelems[name]
                flowelems.append(flowelement(eid,name,comment))

                data=data.split()

                if ('csf' in elemtype): #pour les splines, lire toute les lignes
                    nlines=int(data[0])

                    for j in range(nlines):
                        line=f.readline()

            #flowelems['AHS_Flow_Element']=flowelement(0,'AHS_flow_element','AHS virtual element')
            #flowelems[0]=flowelems['AHS_Flow_Element']
            flowelems.append(flowelement(0,'AHS_flow_element','AHS virtual element'))


            f.close()
            return (flowelems)


def getflowpaths(fname):
        
    flowpaths=[]
    f=open(fname,'r',errors='ignore')
    line=True
       
    while (line):
        line=f.readline()
 
        if ('flow paths:' in line):

            npaths=int(line.split()[0])
            headers=f.readline()
        
            for i in range(npaths):
                line=f.readline()
                line=line.split()

                n=int(line[0])
                flowelemid=int(line[4])

                height=float(line[13])

                mult=float(line[14])
                wp=int(line[15])

                windex=int(line[6])

                WSM=float(line[16])
                
                azim=int(line[17])

                fromzone=int(line[2])
                tozone=int(line[3])

                sketchdir=int(line[22])



                #def __init__(self,number,elemid,fromzone,tozone,multiplier,azimuth,windpressure,windmodifier):
                flowpaths.append(flow_path(n,flowelemid,fromzone,tozone,mult,azim,windex,wp,WSM,sketchdir,height))


            f.close()
            return (flowpaths)


        
    


    


#####!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def getcommonpaths(flowpaths,roomid1,roomid2):
    #DONT CHANGE THIS ONE? THIS IS USED IN CHECK AND SET MODELS
    return flowpaths.df[ ( flowpaths.df['pzn'].isin([roomid1,roomid2]) ) & ( flowpaths.df['pzm'].isin([roomid1,roomid2]) ) ]
##!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def getzoneid(zonename,zonesdf):

    if (zonename in list(zonesdf['name'])):

        return zonesdf[zonesdf['name']==zonename].index[0]

    else:
        return 'Not found'

def getcommonpathsByName(roomname1,roomname2,zonesdf,flowpaths):

    roomid1=getzoneid(roomname1,zonesdf)
    roomid2=getzoneid(roomname2,zonesdf)

    return flowpaths.df[ ( flowpaths.df['pzn'].isin([roomid1,roomid2]) ) & ( flowpaths.df['pzm'].isin([roomid1,roomid2]) ) ]


def getroompaths(roomid,flowpaths):
    
    #input id, returns id
    
    return flowpaths[ (flowpaths['pzn']==roomid) | (flowpaths['pzm']==roomid)]

def getroompathsByName(roomname,zonesdf,flowpathsdf):
    
    #input names, return paths
    roomid=getzoneid(roomname,zonesdf)
    paths=getroompaths(roomid,flowpathsdf)

    return paths


def getroomNTpathsByName(roomname,zonesdf,flowpathsdf,flowelemsdf):

    roompaths=getroompathsByName(roomname,zonesdf,flowpathsdf)
    elemid=flowelemsdf[flowelemsdf['name']=='Gen_NT'].index[0]
    roompaths=roompaths[roompaths['pe']==elemid]

    return roompaths

def getNeighboursNamesWithNT(roomname,zonesdf,flowpathsdf,flowelemsdf):

    roompaths=getroomNTpathsByName(roomname,zonesdf,flowpathsdf,flowelemsdf)
    
    roomid=getzoneid(roomname,zonesdf)

    idpairs = [ [roompaths.loc[i,'pzm'],roompaths.loc[i,'pzn']] for i in roompaths.index ]
    [ x.remove(roomid) for x in idpairs] #will remove zoneid from each x in pairs
     
    
    neighbournames=[ zonesdf.loc[x[0],'name'] for x in idpairs ]

          
    return neighbournames

def getcommonNTpathsByName(roomname1,roomname2,zonesdf,flowpathsdf,flowelemsdf):

    roomid1=getzoneid(roomname1,zonesdf)
    roomid2=getzoneid(roomname2,zonesdf)

    fp=flowpathsdf[ ( flowpathsdf['pzn'].isin([roomid1,roomid2]) ) & ( flowpathsdf['pzm'].isin([roomid1,roomid2]) ) ]

    elemid=flowelemsdf[flowelemsdf['name']=='Gen_NT'].index[0]

    return fp[fp['pe']==elemid]
    
    



def reversepath(flowpaths,fpid):

    reversdirdict={1:4,4:1,2:5,5:2}

    fromroomid=flowpaths.df.loc[fpid,'pzn']
    toroomid=flowpaths.df.loc[fpid,'pzm']
    
    flowpaths.df.loc[fpid,'dir']=reversdirdict[flowpaths.df.loc[fpid,'dir']]
    
    
    
    flowpaths.df.loc[fpid,'pzn']=toroomid
    flowpaths.df.loc[fpid,'pzm']=fromroomid
    

"""def getroompaths(flowpathdf,roomname):

    mask1=[ roomname in x for x in flowpathdf['From zone'] ]
    mask2=[ roomname in x for x in flowpathdf['To zone']]
    mask=np.array(mask1) + np.array(mask2)
    return(flowpathdf[mask])
"""

# def commonpathsByName(zonesdf,flowpathdf,room1,room2):

    # roomid1=zonesdf[zonesdf['name']==room1].index[0]
    # roomid2=zonesdf[zonesdf['name']==room1].index[0]
    
    
    # room1flowpaths=getroompaths(flowpathdf,room1)    
    # commonflowpaths=getroompaths(room1flowpaths,room2)
    
    # return(commonflowpaths)

# def commonpaths(flowpathdf,roomid,room2):

    # room1flowpaths=getroompaths(flowpathdf,room1)
    
    # commonflowpaths=getroompaths(room1flowpaths,room2)
    
    # return(commonflowpaths)

    



def getwindprofiles(fname):
    
    windprofiledf=pd.DataFrame()
    f=open(fname,'r',errors='ignore')
    line=True
       
    while (line):
        line=f.readline()
 
        if ('wind pressure profiles:' in line):
            nprofiles=int(line.split()[0])
            
            for i in range(nprofiles):
                line=f.readline()
               
                id,npoints,type,name=line.split()
                description=f.readline()
               
                windprofiledf.loc[int(id),'Name']=name
                windprofiledf.loc[int(id),'Description']=description
                
               
                for p in range(int(npoints)):
                    line=f.readline()
                    
                    
            f.close()
            
            windprofiledf.loc[0,'Name']='No wind profile'
            
            return windprofiledf
            

def getoccupancyprofiles(fname):
    
    f=open(fname,'r',errors='ignore')
    line=True

    #Get zones names as dataframe
    #--------------------------------------------
    zones=getzones(fname)   
    zonesdf=pd.DataFrame()

    for zone in zones:
        zonesdf.loc[zone.zid,'Name']=zone.name
        zonesdf.loc[zone.zid,'volume']=zone.vol
    #--------------------------------------------

    occupancy_schedules=[]
       
    while (line):
        line=f.readline()

        if ('occupancy schedules:' in line):
            nschedules=int(line.split()[0])

            
            for i in range(nschedules):

                df=pd.DataFrame()

                line=f.readline()
                profilid,nlines,dummy,profilename=line.split()            
                description=f.readline()
                nlines=int(nlines)
                
                
                schedule=occupancy_schedule(int(profilid),profilename,description,df)
                
                
                for l in range(nlines):
                    line=f.readline().split()
                    schedule.addline(line[0].strip(),zonesdf.loc[int(line[1]),'Name'])

                occupancy_schedules.append(schedule)
            f.close()
            return occupancy_schedules



def geticons(fname):

    #most of code copied from "getlevels" --> should consider merging both later

    f=open(fname,'r',errors='ignore')
    line=True

    leveldf=pd.DataFrame()

    leveldf['polygons']=pd.Series(dtype='object')

    levelicons={}

    while(line):
    
        line=f.readline()
        
        if ('levels plus icon data' in line):

            nlevels=int(line.split()[0])

            
            line=f.readline() #headers
            
            for i in range(nlevels):
                line=f.readline()
                fields=line.split()
                name=fields[6]
                deltaH=float(fields[2])
                refH=float(fields[1])
                levelid=int(fields[0])
                
                leveldf.loc[levelid,'Name']=name
                leveldf.loc[levelid,'refH']=refH
                leveldf.loc[levelid,'deltaH']=deltaH
                
                nicons=int(fields[3])
                
                f.readline() #ico headers


                levelicons[levelid]=pd.DataFrame()

                for ico in range(nicons):
                    line=f.readline()
                    icn,col,row,elemid=line.split()
                    levelicons[levelid].loc[ico,'icn']=icn
                    levelicons[levelid].loc[ico,'col']=col
                    levelicons[levelid].loc[ico,'row']=row
                    levelicons[levelid].loc[ico,'elemid']=elemid
                 
                levelpolygons=readlevelicons(levelid,levelicons[levelid].astype(int))

                
 
                if (levelpolygons != None):
                    leveldf.at[levelid,'polygons']=levelpolygons
                else:
                    leveldf.at[levelid,'polygons']=[]
                
                #print("Level ID",levelid)
                #print(levelicons[levelid])
            
            f.close()
            
            leveldf=leveldf.reindex(columns=['Name','refH','deltaH','polygons'])
            
            return leveldf,levelicons


def readlevelicons(levelid,iconsdf):
    
    pd.options.mode.chained_assignment = 'raise'
    
    if (iconsdf.empty):
        return
        
    corners=iconsdf[iconsdf['elemid']==0]

    if (corners.empty):
        return


    newcols=['right','left','up','down']
    
    searchdirs={
        14:['down','right'],
        15:['left','down'],
        16:['left','up'],
        17:['up','right'],
        18:['up','down','right'],
        19:['down','left','right'],
        20:['up','down','left'],
        21:['up','left','right'],
        22:['right','left','up','down']
    }
    
    for c in newcols:
        #corners.loc[:,c]=np.nan
        #corners[c]=np.nan
        corners=corners.assign(c=np.nan)

    edges=[]
    edges=pd.DataFrame(columns=['from','to','dir'])
    edgecount=1

    

    for i in corners.index:

        for dir in searchdirs[corners.loc[i,'icn']]:
            
            row=corners.loc[i,'row']
            col=corners.loc[i,'col']
    
            #print("Id: ",i ,"row ",row," col ",col)
            #print("Direction ",dir)
            
            if dir == 'right':
                candidates=corners[ (corners['row']==row) & (corners['col']>col) ]
                candidates=candidates.assign(distance = abs(candidates.loc[:,'col']-col))               

            if dir == 'left':
                candidates=corners[ (corners['row']==row) & (corners['col']<col) ]
                #candidates.loc[:,'distance']=abs(candidates.loc[:,'col']-col)               
                candidates=candidates.assign(distance = abs(candidates.loc[:,'col']-col))               


            if dir == 'up':
                candidates=corners[ (corners['row']<row) & (corners['col']==col) ]
                #candidates.loc[:,'distance']=abs(candidates.loc[:,'row']-row)
                candidates=candidates.assign(distance= abs(candidates.loc[:,'row']-row))

            if dir == 'down':
                candidates=corners[ (corners['row']>row) & (corners['col']==col) ]
                #candidates.loc[:,'distance']=abs(candidates.loc[:,'row']-row)
                candidates=candidates.assign(distance= abs(candidates.loc[:,'row']-row))


            neighbourid=candidates['distance'].idxmin()

            #edges.append([i,neighbourid,dir])
            edges.loc[edgecount,:]=[i,neighbourid,dir]
            edgecount+=1
            
            corners.loc[i,dir]=neighbourid
    
 
    dirs=['down','right','up','left']
 
    angles={
        'down':270,
        'right':0,
        'up':90,
        'left':180
        }   
        
    edges.loc[:,'angle']=[ angles[i] for i in edges['dir']]
 
    edgesid=list(edges.index)
    startpointslist=list(corners.index)
 
 
    currentdir=itertools.cycle(dirs)
 
    allpolys=[]
 
    while (len(edgesid) > 0 ):

        polystartpoint=startpointslist[0]
        newstartpoint=polystartpoint
        startpointslist.remove(newstartpoint)

        poly=[polystartpoint]

        previousangle=180 #set a first reference
        polyclosed=False

        polytotalangle=0
        
        while (polyclosed==False):

            edgesfromstartpoint=edges.loc[edgesid,:]                                                    #retain only remaining edges
            edgesfromstartpoint=edgesfromstartpoint[edgesfromstartpoint['from']==newstartpoint]         #retain only the ones staring by the startpoint

            if (edgesfromstartpoint.empty):
                #print("No new room starting from this point")
                break
            
            #print(poly)
            if(len(poly)>1):
                edgesfromstartpoint=edgesfromstartpoint[edgesfromstartpoint['to']!=poly[-2]]          #prevent going back

            edgesfromstartpoint['angle-variation']=(edgesfromstartpoint['angle']-previousangle)%360     
            edgesfromstartpoint.loc[edgesfromstartpoint['angle-variation']>=180,'angle-variation'] += -360
            
            #all back in  -180 +180 inteval
            #ideal direction is +90 --> maximum left rotation since 180 is excluded with the "prevent going back"

            #possible values: 90, 0 or 270 (--> 90 = left, 0 --> straight ahead , 270 --> right)


            nextedge=edgesfromstartpoint['angle-variation'].idxmax()
            nextpoint=edgesfromstartpoint.loc[nextedge,'to']
            nextangle=edgesfromstartpoint.loc[nextedge,'angle-variation']
            polytotalangle+=nextangle
           
            #print("Edge",nextedge)
            #print("Nextpoint ",nextpoint)

            previousangle=edges.loc[nextedge,'angle']   


            if (nextpoint==polystartpoint):
                polyclosed=True
                if polytotalangle == 360:
                    type='room'
                else:
                    type='building'
                allpolys.append({'points':poly,'type':type})
                #print("Latest polygon ",poly)
                #print("Cumulated rotation angle",polytotalangle)
            else:

                poly.append(nextpoint)
                newstartpoint=nextpoint
            
            edgesid.remove(nextedge)
        
        

    #all polys = polygon by nodes
    for polygon in allpolys:
    
        if (polygon['type']=='room'):
        
            polygon['xy']=[]
            for nodeid in polygon['points']:
                row=corners.loc[nodeid,'row']
                col=corners.loc[nodeid,'col']
                polygon['xy'].append([row,col])
                
    #print("Detected polygons")
    #[ print (x) for x in allpolys ]

    
    zones=iconsdf[ iconsdf['icn'].isin([5,6]) ]  # 5 = icon number for zones ; 6 = icon number for phantom zones

    for index in zones.index:

        points=[[zones.loc[index,'row'],zones.loc[index,'col']]]
        
        for polygon in allpolys:
        
            if (polygon['type']=='room'):
                path = mplPath.Path(polygon['xy'])
                inside2 = path.contains_points(points)

                if (inside2[0]):
                    polygon['roomid']=zones.loc[index,'elemid']
                    
    
    
    #print(allpolys)
    return allpolys





