import sys
sys.path.append('/home/spec/Documents/Projects/RESEARCH/COMISVENT/2.Work/Python')

import contam_functions
import pandas as pd
import json
import math
import cairo
import numpy as np

import argparse



parser = argparse.ArgumentParser(description='Draw a building and its ventilation system from CONTAM prj file')
parser.add_argument('contamPRJ',help='CONTAM prj file to draw')  
parser.add_argument('-outputFormat', default='png',choices=['png','pdf','svg'], help='Output file format for drawing (default:png)')
parser.add_argument('-drawCracks',  action='store_true', help='Draw cracks')
parser.add_argument('-drawTransfers',  action='store_true', help='Draw natural transfer between rooms')
parser.add_argument('-NoFlows', action='store_true', help='Do not write flow rates/capacity next to devices (drawed by default)')


args=parser.parse_args()

contamfile=args.contamPRJ
outputformat=args.outputFormat



#-------------------------
# Defining draw functions
#-------------------------

def drawarrow(ctx,x,y,rotation,color,text,writeFlow=True):

# by default, draw arrow towards bottom (--> ok for natural supply vent with AZM = 0)
# --> for NSV with other directions, should be rotated of the wall azm to remain consistent

# x , y : center of arrow position
# defaut size of arrow = height = 6, width = 4
# direction: up, down, right, left
# ctx = cairo context

    ctx.translate(x,y)
    ctx.rotate(np.radians(rotation))
    
    ctx.move_to(0,5)
    ctx.line_to(-2,2)
    ctx.line_to(-1,2)
    ctx.line_to(-1,-4)
    ctx.line_to(1,-4)
    ctx.line_to(1,2)
    ctx.line_to(2,2)
    ctx.close_path()
   
   
    if color=='green':
   
        ctx.set_source_rgb(112/255, 173/255, 71/255) # lightgreen
        ctx.fill_preserve()
        ctx.set_source_rgb(80/255, 126/255, 50/255) # darker green
        ctx.set_line_width(0.1)
        ctx.stroke()

    if color=='red':
    
        ctx.set_source_rgb(246/255, 66/255, 10/255) # lightred
        ctx.fill_preserve()
        ctx.set_source_rgb(181/255, 46/255, 5/255) # darker red
        ctx.set_line_width(0.1)
        ctx.stroke()

  
    
    ctx.set_source_rgb(0,0,0) 
       
    ctx.select_font_face("Arial",
                     cairo.FONT_SLANT_NORMAL,
                     cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(1)

    xbearing, ybearing, width, height, dx, dy = ctx.text_extents(text)
    ctx.move_to(0+width/2,-3)

    #unrotate before writing
    ctx.rotate(-np.radians(rotation))


    #Writing flow rate

    if (writeFlow):
    
        ctx.show_text(text)

    ctx.translate(-x,-y)
    
   

def drawtransfer(ctx,x,y,rotation):

# by default, draw arrow towards bottom (--> ok for natural supply vent with AZM = 0)
# --> for NSV with other directions, should be rotated of the wall azm to remain consistent

# x , y : center of arrow position
# defaut size of arrow = height = 6, width = 4
# direction: up, down, right, left
# ctx = cairo context

    ctx.translate(x,y)
    ctx.rotate(np.radians(rotation))
    
    scale=0.5
    ctx.scale(scale,scale)
    
    ctx.move_to(0,5)
    ctx.line_to(-2,2)
    ctx.line_to(-1,2)
    ctx.line_to(-1,-2)
    ctx.line_to(-2,-2)
    ctx.line_to(0,-5)
    ctx.line_to(2,-2)
    ctx.line_to(1,-2)
    ctx.line_to(1,2)
    ctx.line_to(2,2)
    ctx.close_path()
   
    ctx.set_source_rgb(149/255, 200/255, 216/255) # lightblue
    ctx.fill_preserve()
    
    ctx.set_source_rgb(87/255, 160/255, 211/255) # darker green

    ctx.set_line_width(0.1)
    ctx.stroke()

    ctx.scale(1/scale,1/scale)

    ctx.rotate(-np.radians(rotation)) # first unrotate before untranslate
    ctx.translate(-x,-y)


def drawcornerarrow(ctx,x,y,rotation):

# by default, draw arrow towards bottom (--> ok for natural supply vent with AZM = 0)
# --> for NSV with other directions, should be rotated of the wall azm to remain consistent

# x , y : center of arrow position
# defaut size of arrow = height = 6, width = 4
# direction: up, down, right, left
# ctx = cairo context

    ctx.translate(x,y)
    ctx.rotate(np.radians(rotation))
    
    scale=0.5
    ctx.scale(scale,scale)
    
    ctx.move_to(1,5)
    ctx.line_to(-1,2)
    ctx.line_to(0,2)
    ctx.line_to(0,0)
    ctx.line_to(-2,0)
    ctx.line_to(-2,1)
    ctx.line_to(-5,-1)
    ctx.line_to(-2,-3)
    ctx.line_to(-2,-2)
    ctx.line_to(2,-2)
    ctx.line_to(2,2)
    ctx.line_to(3,2)
    ctx.close_path()
   
    ctx.set_source_rgb(149/255, 200/255, 216/255) # lightblue
    ctx.fill_preserve()
    
    ctx.set_source_rgb(87/255, 160/255, 211/255) # darker green

    ctx.set_line_width(0.1)
    ctx.stroke()

    ctx.scale(1/scale,1/scale)
    ctx.rotate(-np.radians(rotation)) # first unrotate before untranslate
    ctx.translate(-x,-y)



def drawfan(ctx,xc,yc,nblades,width):

    # basic drawing fan has width of 12 px
    # width is there to scale it to desired size

    scale=width/12

    increment=360/nblades


    ctx.set_source_rgb(0,0,0) #black
    w=12.0*scale
    ctx.rectangle(xc-w/2,yc-w/2,w,w)
    ctx.fill()

    ctx.set_source_rgb(1,1,1) # white
    ctx.arc(xc, yc, 5.5*scale, 0, 2*np.pi)
    ctx.close_path()
    ctx.fill()

    ctx.set_source_rgb(0,0,0) #black

    for i in range(nblades):
        drawblade(ctx,xc,yc,i*increment,scale)

    #blade = H=5

    ctx.set_source_rgb(0,0,0) # black
    ctx.arc(xc, yc, 1.5*scale, 0, 2*np.pi)
    ctx.close_path()
    ctx.fill()

    ctx.set_source_rgb(1,1,1) # white
    ctx.arc(xc, yc, 1.0*scale, 0, 2*np.pi)
    ctx.close_path()
    ctx.fill()

    ctx.set_source_rgb(0,0,0) # white
    ctx.arc(xc, yc, 0.5*scale, 0, 2*np.pi)
    ctx.close_path()
    ctx.fill()



def drawblade(ctx,xc,yc,rotation,scale):

    ctx.translate(xc,yc)
    ctx.rotate(np.radians(rotation)) # first unrotate before untranslate

    control_scale=0.5

    pxy=[]
    
    pxy.append(np.array([0,0]))
    pxy.append(np.array([-1,1]))
    pxy.append(np.array([-1.5,3.0]))
    pxy.append(np.array([-1,4.35]))

    pxy.append(np.array([0,5]))
 
 
    pxy.append(np.array( [-pxy[3][0],pxy[3][1]] ) )
    pxy.append(np.array( [-pxy[2][0],pxy[2][1]] ) )
    pxy.append(np.array( [-pxy[1][0],pxy[1][1]] ) )

    pxy.append(np.array([0,0]))

    dxdy=[]

    dxdy.append(np.array([-0.25,0.25])) #0
    dxdy.append(np.array([-0.25,0.50])) #1
    dxdy.append(np.array([ 0.00,0.50])) #2
    dxdy.append(np.array([ 0.25,0.50])) #3 
    dxdy.append(np.array([ 0.25,0.00])) #4
    dxdy.append(np.array([ 0.25,-0.50])) #5
    dxdy.append(np.array([ 0.00,-0.50])) #6
    dxdy.append(np.array([-0.25,-0.50])) #7
    dxdy.append(np.array([-0.25,-0.25])) #8

    for i in range(len(dxdy)):
        dxdy[i]=dxdy[i]/np.linalg.norm(dxdy[i])*control_scale


    #setting everything to scale coming from upper
    dxdy=[ x*scale for x in dxdy]
    pxy=[x*scale for x in pxy]
    

    ctx.move_to(pxy[0][0],pxy[0][1])
    
    
    for i in range(8):
        #print( pxy[i][0]+dxdy[i][0] , pxy[i][1]+dxdy[i][1] , pxy[i+1][0]-dxdy[i+1][0] )#, pxy[i+1][1]-dxdy[i+1][1] , pxy[i+1][0] , pxy[i+1][1]) #1
        
        ctx.curve_to( pxy[i][0]+dxdy[i][0] , pxy[i][1]+dxdy[i][1] , pxy[i+1][0]-dxdy[i+1][0] , pxy[i+1][1]-dxdy[i+1][1] , pxy[i+1][0] , pxy[i+1][1]) #1
    

    ctx.close_path()


    #ctx.curve_to(-1,4,-2.5,1,-1,4)   #3
    #ctx.curve_to(0,5,-1,4,0,5)

    ctx.fill_preserve()
    ctx.stroke()

    ctx.rotate(-np.radians(rotation)) # first unrotate before untranslate
    ctx.translate(-xc,-yc)
    
def drawcrack(ctx,x,y,rotation,color):

    ctx.translate(x,y)
    ctx.rotate(np.radians(rotation))

    ctx.scale(0.5,0.5)
    
    ctx.move_to(-0.5,-2.5)

    ctx.line_to(0.5,-1.5)
    ctx.line_to(-0.5,-0.5)
    ctx.line_to(0.5,0.5)
    ctx.line_to(-0.5,1.5)
    ctx.line_to(0.5,2.5)
   
    if (color=='red'):
        ctx.set_source_rgb(1,0,0) # red
    elif(color=='purple'):
        ctx.set_source_rgb(1,0,1) # purple
    elif (color=='blue'):
        ctx.set_source_rgb(0,0,1) # blue
        

    ctx.set_line_width(0.2)
    ctx.stroke()

    ctx.scale(2,2)
    ctx.rotate(-np.radians(rotation)) # first unrotate before untranslate
    ctx.translate(-x,-y)


# ----------------------------------
# Load CONTAM FILE and various parts
# ----------------------------------

# legacy levels and icons reader, but allows to get polygons of the rooms (not included in the current reader)
legacyleveldf,levelicons=contam_functions.geticons(contamfile)


# current readers
contam_data=contam_functions.loadcontamfile(contamfile)
levels=contam_data['levels']
zones=contam_data['zones']
flowpaths=contam_data['flowpaths']
flowelems=contam_data['flowelems']
contaminants=contam_data['contaminants']
ahs=contam_data['ahs']
controls=contam_data['controls']

AHSreturn=ahs.df.loc[1,'zr#']
AHSsupply=ahs.df.loc[1,'zs#']



#---------------------------------
#Check dimensions of the building
#---------------------------------

bounds={'minx':100,
        'maxx':0,
        'miny':100,
        'maxy':0
        }




for level in levels.df.index:

    rooms=legacyleveldf.polygons[level]
    
    
    for room in rooms:

        print(room)

    
        if (room['type']=='room'):

            for i in range(len(room['xy'])):

                y,x=room['xy'][i]   # invert x and y because they are inverted in the reader...
                
                bounds['maxx']=np.max([bounds['maxx'],x])
                bounds['maxy']=np.max([bounds['maxy'],y])
                bounds['minx']=np.min([bounds['minx'],x])
                bounds['miny']=np.min([bounds['miny'],y])
  
bounds['dx']=bounds['maxx']-bounds['minx']
bounds['dy']=bounds['maxy']-bounds['miny']

#print(bounds)




#----------------
# Loop on levels
#----------------

for level in levels.df.index:

    rooms=legacyleveldf.polygons[level]
    #allicons=levelicons[level]

    if (len(rooms)==0):
        print("No rooms on this level ("+str(level)+"), skipping")
        continue    

    #-----------------------
    # Start drawing
    #-----------------------


    WIDTH, HEIGHT = bounds['dx']+20, bounds['dy']+20

    
    if ('png' in outputformat):
        scale=30
        ps = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH*scale, HEIGHT*scale)
    elif (outputformat=='pdf'):
        ps = cairo.PDFSurface(contamfile.replace('.prj','-'+str(level)+'.pdf'), WIDTH,HEIGHT)
    elif (outputformat=='svg'):
        ps = cairo.SVGSurface(contamfile.replace('.prj','-'+str(level)+'.svg'), WIDTH,HEIGHT)
    else:
        print("Unknown file format")


    ctx = cairo.Context(ps)
    
    if ('png' in outputformat):
        ctx.scale(scale,scale)
    
    ctx.translate(-bounds['minx']+10,-bounds['miny']+10)

    #ctx.scale(WIDTH, HEIGHT)  # Normalizing the canvas


    redfill = cairo.SolidPattern(1.0,0.0,0.0,1.0)
    greenfill = cairo.SolidPattern(0.0,1.0,0.0,1.0)
    bluefill = cairo.SolidPattern(0.0,0.0,1.0,1.0)
    whitefill = cairo.SolidPattern(0.0,0.0,0.0,1.0)


    #-------------
    #Drawing rooms
    #-------------

    for room in rooms:
    
        roombbox={'minx':100,
                  'maxx':0,
                  'miny':100,
                  'maxy':0,}
    
        if (room['type']=='room'):

            for i in range(len(room['xy'])):

            
                y,x=room['xy'][i]   # invert x and y because they are inverted in the reader...
                
                roombbox['maxx']=np.max([roombbox['maxx'],x])
                roombbox['maxy']=np.max([roombbox['maxy'],y])
                roombbox['minx']=np.min([roombbox['minx'],x])
                roombbox['miny']=np.min([roombbox['miny'],y])
  
                
                if i==0:
                    ctx.move_to(x,y)

                else:
                    ctx.line_to(x,y)

            ctx.close_path()
            
            
            ctx.set_source_rgb(0, 0, 0) # black
            ctx.set_line_width(0.2)
            ctx.stroke()

            ctx.select_font_face("Arial",
                         cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_NORMAL)
            ctx.set_font_size(1)


            roomname=zones.df.loc[room['roomid'],'name']

            xbearing, ybearing, width, height, dx, dy = ctx.text_extents(roomname)
            ctx.move_to((roombbox['minx']+roombbox['maxx']-width)/2,(roombbox['miny']+roombbox['maxy']-height)/2)

            ctx.show_text(roomname)



    #-----------------------------------
    # Drawing Natural devices
    #-----------------------------------

    #for icon in allicons[allicons['icn']=='23'].index:
    for flowpathid in flowpaths.df[flowpaths.df['icon']==23].index:
    
        if (flowpaths.df.loc[flowpathid,'pld'] != level and not (flowpaths.df.loc[flowpathid,'pld']==level+1 and (flowpaths.df.loc[flowpathid,'dir']==6)) ):
        
            continue
        #flowpathid=allicons.loc[icon,'elemid']
        
        junctionlevel=flowpaths.df.loc[flowpathid,'pld']  #for junctions that are defined from the top !
        
        allicons=levelicons[junctionlevel] #all incons of this level
        icon=allicons[allicons['elemid']==str(flowpathid)].index[0]
        
        flowelemid=flowpaths.df.loc[int(flowpathid),'pe']
        
        flowelemname=flowelems.df.loc[flowelemid,'name']
        
        azm=flowpaths.df.loc[int(flowpathid),'wazm']
        
        flow=str(int(round(float(flowpaths.df.loc[int(flowpathid),'mult']),0)))


        #determining rotation

        rotationdict={1:180,2:270,4:0,5:90,3:90,6:90}

        sketchdirection=flowpaths.df.loc[int(flowpathid),'dir']
    
        rotation=rotationdict[sketchdirection]
        
        #sketchdirs={1:'S',2:'W',4:'N',5:'E'}
        #     if(flowpaths.df.loc[int(flowpathid),'dir'] in [2,5]):
        #        rotation=90


  
         
        if ('NSV_' in flowelemname):
            
            drawarrow(ctx,int(allicons.loc[icon,'col']),int(allicons.loc[icon,'row']),rotation,'green',flow,not args.NoFlows)
            
        if ('NT_' in flowelemname and args.drawTransfers):
        
            if(flowpaths.df.loc[int(flowpathid),'dir'] in [2,5]):
                rotation=90
                drawtransfer(ctx,int(allicons.loc[icon,'col']),int(allicons.loc[icon,'row']),rotation)

            elif(flowpaths.df.loc[int(flowpathid),'dir'] in [1,4]):
                rotation=0
                drawtransfer(ctx,int(allicons.loc[icon,'col']),int(allicons.loc[icon,'row']),rotation)

            elif(flowpaths.df.loc[int(flowpathid),'dir'] in [3,6]):
                drawcornerarrow(ctx,int(allicons.loc[icon,'col']),int(allicons.loc[icon,'row']),90)



        if ('crack' in flowelemname and args.drawCracks):
        
            if(flowpaths.df.loc[int(flowpathid),'dir'] in [1,2,4,5]):
                color='red'

            if(flowpaths.df.loc[int(flowpathid),'dir'] in [3]):
                color='purple'

            if(flowpaths.df.loc[int(flowpathid),'dir'] in [6]):
                color='blue'

            drawcrack(ctx,int(allicons.loc[icon,'col']),int(allicons.loc[icon,'row']),int(azm),color)


    #-------------------------------
    # Drawing mechanical devices
    #-------------------------------



    allicons=levelicons[level]
    #Option 1: place on the location of the return/supply object

    for fpid in flowpaths.df.index:

        if ( flowpaths.df.loc[fpid,'pld']==level and flowpaths.df.loc[fpid,'icon'] in [128,129] and float(flowpaths.df.loc[fpid,'Fahs'])>0  ):

            
            iconindex=allicons[allicons['elemid']==str(fpid)].index[0]
            
            fromto=list(flowpaths.df.loc[fpid,['pzm','pzn']])
            
            flow=str(int(round(float(flowpaths.df.loc[fpid,'Fahs'])/1.2041*3600,0)))

            if (AHSreturn in fromto):
                fromto.remove(AHSreturn)
                color='red'
            if (AHSsupply in fromto):
                fromto.remove(AHSsupply)
                color='green'
       

            #print(flowpaths.df.loc[fpid,:])
            drawarrow(ctx,int(allicons.loc[iconindex,'col']),int(allicons.loc[iconindex,'row']),180,color,flow, not args.NoFlows)       
            drawfan(ctx,int(allicons.loc[iconindex,'col']),int(allicons.loc[iconindex,'row']),3,2.5)



    #Option 2: look for an unused natural opening in the same space, and using it as locator
    # !if there is one!! --> otherwise, just use locator

    """for fpid in flowpaths.df.index:

        if ( flowpaths.df.loc[fpid,'pld']==level and flowpaths.df.loc[fpid,'icon'] in [128,129] and float(flowpaths.df.loc[fpid,'Fahs'])>0  ):

            fromto=list(flowpaths.df.loc[fpid,['pzm','pzn']])

            if (AHSreturn in fromto):
                fromto.remove(AHSreturn)
                color='red'
            if (AHSsupply in fromto):
                fromto.remove(AHSsupply)
                color='green'
            
            zonesextfp=flowpaths.df[ (flowpaths.df['pzm']==fromto[0]) & (flowpaths.df['pzn']==-1) ]

            #on choisit un qui a un multiplicateur 0, comme ca on est sur qu'il ne sert a rien

            if(len(zonesextfp[ (zonesextfp['mult']=='0.0') ].index)>0):
                fakefpid=zonesextfp[ (zonesextfp['mult']=='0.0') ].index[0]
            else:
                fakefpid=fpid
            
            
            iconindex=allicons[allicons['elemid']==str(fakefpid)].index[0]
            drawarrow(ctx,int(allicons.loc[iconindex,'col']),int(allicons.loc[iconindex,'row']),180,color)       
            drawfan(ctx,int(allicons.loc[iconindex,'col']),int(allicons.loc[iconindex,'row']),3,2.5)
    """
            
       

    if ('png' in outputformat):
        ps.write_to_png(contamfile.replace('.prj','-'+str(level)+'.png'))


















