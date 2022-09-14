
import contam_functions
import pandas as pd
import numpy as np
import datetime

import os

def apply(contam_data,occupancy_profile,profilesDir):

    
    #options: default = NSlaapkamers + 1 occupant
    # 2 adults, other are childs


    # ----------------------------------
    # Load CONTAM FILE and various parts
    # ----------------------------------

    zones=contam_data['zones']
    controls=contam_data['controls']
    oschedules=contam_data['oschedules']
    dayschedules=contam_data['dayschedules']
    weekschedules=contam_data['weekschedules']
    exposures=contam_data['exposures']
    
    sourceElems=contam_data['sourceelems']
    sources=contam_data['sources']

    #Determining number of slaapkamers
    
    zoneslist=list(contam_data['zones'].df['name'])
    
    boolarray=['Slaapkamer' in x for x in list(contam_data['zones'].df['name']) ]
    slaaplist=list(contam_data['zones'].df.loc[boolarray,'name'])
    nslaap = len(slaaplist) 
    

    if len(zoneslist) == 3 :
        print("Only a single zone in the model, skipping occupancy and sources definition")
        return 

    ###########################
    # DAY SCHEDULES/OCCUPANCY #
    ###########################

    #defaut hypothesis: nslaap+1 occupants
    dosdict={} #day occupancy schedules day dictionnary text_key:id
    #dsdict={} # day schedules dictionnary text_key:id 
    
    co2scheduledict={} # occupancy schedule id : CO2 schedule id
    h2oscheduledict={} # occupancy schedule id:  H2O schedule id
    
    for oid in range(1,nslaap+2):
        
        for ptype in ['Home','Busy','Away']:

            fname=os.path.join(profilesDir,'profile_Occupant'+str(oid)+'_'+ptype+'.csv')
        
            if (not os.path.exists(fname)):
                #print(fname+" does not exist, skipping")
                continue
        
            #Reading standard profile 
            name,des,df=read_standard_occupancy_file(fname)

            slaapkamerName='Slaapkamer'

            sortedbedrooms=list(zones.df[zones.df['name'].str.contains('Slaapkamer')].sort_values(by='Vol',ascending=False)['name'])


            biggestbedroom=sortedbedrooms[0]
            sortedbedrooms.remove(biggestbedroom)


            if (oid <3):
                slaapkamerName=biggestbedroom

            elif (oid>2):
                slaapkamerName=sortedbedrooms[oid-3]
                
                #else : oid<3 and Slaapkamer1 not in slaaplist ) --> do nothing

            df.replace('Slaapkamer',slaapkamerName,inplace=True)

            if ('OKeuken' in zoneslist):
                df.replace('Keuken','OKeuken',inplace=True)

            if ('WC' not in zoneslist):
                df.replace('WC','Badkamer',inplace=True)


            zonesid=[ contam_functions.getzoneid(x,contam_data['zones'].df) if x!='ext' else -1 for x in df['zonename'] ]
            df['zid']=zonesid 

            # add day occupancy schedule for occupant
            oschedules.addSchedule(name,des,df)
            scheduleid=oschedules.getLastId()
            
            dosdict['O'+str(oid)+'_'+ptype]=scheduleid

            # create corresponding CO2 and H2O emission schedules 
            slaapkamerid=contam_functions.getzoneid(slaapkamerName,contam_data['zones'].df)  #bedroom ID of the occupant
            
            #print(slaapkamerid)
            
            co2schedule=oschedules.genEmissionSchedule(scheduleid,slaapkamerid,0.625)
            dayschedules.addSchedule('CO2_Day_O'+str(oid)+'S'+str(scheduleid),'CO2 emission for occ-profile '+str(scheduleid),co2schedule)

            co2scheduledict[scheduleid]=dayschedules.getLastId()

            h2oschedule=oschedules.genEmissionSchedule(scheduleid,slaapkamerid,0.7)
            dayschedules.addSchedule('H2O_Day_O'+str(oid)+'S'+str(scheduleid),'H2O emission for occ-profile '+str(scheduleid),h2oschedule)

            h2oscheduledict[scheduleid]=dayschedules.getLastId()
        

    ############################
    # WEEK SCHEDULES/OCCUPANCY #
    ############################

    
    for oid in range(1,nslaap+2):
    
        #this should be an input parameter or deduced from a input parameter
        
        if (occupancy_profile=='default-home'):
        
            textschedulelist= [ 'O'+str(oid)+'_'+'Home' for i in range(12) ] #full text list of 12 day schedules 
        
        elif (occupancy_profile=='default-active'):
        
            textschedulelist= [ 'O'+str(oid)+'_'+'Home' if i in [0,6] else 'O'+str(oid)+'_Busy' for i in range(12) ] #full text list of 12 day schedules 
        
        else:
            print("Wrong occupation type ",occupancy_profile)
            print("Exiting")
            return
        
        oweekschedulelist=[ dosdict[x] for x in textschedulelist]            # list of 12 schedules with ids

        co2weekschedule=[co2scheduledict[x] for x in oweekschedulelist]
        h2oweekschedule=[h2oscheduledict[x] for x in oweekschedulelist]
       
        weekschedules.addSchedule('CO2W_O'+str(oid),'CO2 Week schedule for occupant '+str(oid),co2weekschedule)
        co2Wid=weekschedules.getLastId()
               
        
        weekschedules.addSchedule('H2OW_O'+str(oid),'H2O Week schedule for occupant '+str(oid),h2oweekschedule)
        h2oWid=weekschedules.getLastId()

        
        exposures.addExposure('O'+str(oid)+' Exposure',
                                oweekschedulelist,
                                [
                                {'name':'CO2','schedule':co2Wid,'rate':16,'unit':'L/h','value_file':0},
                                {'name':'H2O','schedule':h2oWid,'rate':55,'unit':'g/h','value_file':0}
                                ]
                            )
        
        #should add log
        #def addexposuresensor(self,oid,specie_name,description=''):
        controls.addexposuresensor(oid,'CO2')
        controls.addexposuresensor(oid,'VOC')
       
 
    # Add other H2O sources that are linked with the occupancy profile, but not directly 
    # Bathroom --> douches
    # Kitchen --> morning, dinner, supper
    # Laundry 

 
    schedules_groups=[]

    for daytype in range(12):

        daylist=[]
        schedules_groups.append(daylist)  #cumulated day_profiles

        for oid,v in exposures.exposures.items():
        
            daylist.append(v['day_schedules'][daytype])
            
        # list of list    for each day, a list of all user occupancy profiles  [ [1,2,3,4] , [1,2,3,4] , ...]
        
    unique_groups=set(tuple(row) for row in schedules_groups)
            
    #In most cases: there is one combination for weenkend, and one combination for weedays
            
    bathroomid=contam_functions.getzoneid('Badkamer',zones.df)
    
    if ('Keuken' in list(zones.df['name'])):
        keukenid=contam_functions.getzoneid('Keuken',zones.df)
    else:
        keukenid=contam_functions.getzoneid('OKeuken',zones.df)

    douche_profile_dict={}
    keuken_profile_dict={}
     
    localcounter=1
    
    #from the individual occupancy profiles and their combinations , constructing the bathroom and kitchen profiles 
    # the main idead is: if there is no-one, no sourceElemID
    
    # Implementation details:
    # for each occupant, the moment of the douche is specified in the generic CSV files
    # for the kitche, there is a predefined source profile for each of the 3 meals, if someone is present in the Kitchen in predefined time-slots
    #  someone  6< <9h --> source in the morining
    #  someone  12<14 --> source for lunch
    #  someone 18-20 --> source for the dinner
    
    for group in unique_groups:

        doucheprofile=pd.DataFrame()
        keukenprofile=pd.DataFrame(columns=['hour','value'])
        keukenocc=pd.DataFrame()

        for profileid in group:
            
            moddf=oschedules.schedules[profileid]['dataframe'].copy()
            moddf.index=moddf['hour']
            moddf.drop(['24:00:00'],inplace=True)
            moddf.index=pd.to_datetime(moddf.index)
            
            douchetime=moddf[ (moddf['zid']==bathroomid) & (moddf['douche']==1.0) ].index

            keukenpres= (moddf['zid']==keukenid)
            keukenpres.name=profileid
            keukenocc=pd.concat([keukenocc,keukenpres],axis=1) #1 column per occupant
            
            if (len(douchetime)>0):
                for t in douchetime:
                    #douche 10  min for each individual
                    locprofile=pd.DataFrame(index=[t,t+datetime.timedelta(minutes=10)],columns=[profileid])
                    locprofile.loc[t,profileid]=1.0
                    locprofile.loc[t+datetime.timedelta(minutes=10),profileid]=0.0
                    
                    #adding one column for each indidividual
                    doucheprofile=pd.concat([doucheprofile,locprofile],axis=1)



        doucheprofile.fillna(value=0)
        doucheprofile=doucheprofile.sum(axis=1) #sum of all indidviduals to have a single profile
        doucheprofile.index=[ str(x.time()) for x in doucheprofile.index ] #going back to CONTAM compatible time format
        doucheprofile.loc['00:00:00']=0
        doucheprofile.loc['24:00:00']=0
        doucheprofile.name='value'
        doucheprofile.sort_index(inplace=True)
        doucheprofile=pd.DataFrame(doucheprofile)
        doucheprofile.loc[:,'hour']=doucheprofile.index
        dayschedules.addSchedule('DoucheDay_'+str(localcounter),'Day douche profile for occupancy profiles '+str(group),doucheprofile)  
        contam_day_profile_id=dayschedules.getLastId()
        douche_profile_dict[group]=contam_day_profile_id

        keukenocc=keukenocc.sum(axis=1)

        #print(keukenocc)

        #keukenprofile = keukenprofile.append({'hour':'00:00:00','value':0.0},ignore_index=True)
        keukenprofile = pd.concat([keukenprofile,pd.DataFrame.from_records([{'hour':'00:00:00','value':0}])])
        keukenprofile = pd.concat([keukenprofile,pd.DataFrame.from_records([{'hour':'00:00:00','value':0}])],ignore_index=True)

        
        #morning
        boolindex=( (keukenocc.index.time > datetime.time(6)) & (keukenocc.index.time < datetime.time(9)) )
        if (keukenocc.loc[boolindex].max() > 0 ): #occupation durant la periode
            #keukenprofile=keukenprofile.append({'hour':'07:00:00','value':0.4},ignore_index=True)
            #keukenprofile=keukenprofile.append({'hour':'07:10:00','value':0.0},ignore_index=True)
            keukenprofile = pd.concat([keukenprofile,pd.DataFrame.from_records([{'hour':'07:00:00','value':0.4}])],ignore_index=True)
            keukenprofile = pd.concat([keukenprofile,pd.DataFrame.from_records([{'hour':'07:10:00','value':0.0}])],ignore_index=True)


        #midi
        boolindex=( (keukenocc.index.time >= datetime.time(12)) & (keukenocc.index.time < datetime.time(14)) )
        if (keukenocc.loc[boolindex].max() > 0 ): #occupation durant la periode
            #keukenprofile=keukenprofile.append({'hour':'12:00:00','value':0.4},ignore_index=True)
            #keukenprofile=keukenprofile.append({'hour':'12:10:00','value':0.0},ignore_index=True)
            keukenprofile = pd.concat([keukenprofile,pd.DataFrame.from_records([{'hour':'12:00:00','value':0.4}])],ignore_index=True)
            keukenprofile = pd.concat([keukenprofile,pd.DataFrame.from_records([{'hour':'12:10:00','value':0}])],ignore_index=True)


        #soir
        boolindex=( (keukenocc.index.time >= datetime.time(18)) & (keukenocc.index.time < datetime.time(20)) )
        if (keukenocc.loc[boolindex].max() > 0 ): #occupation durant la periode
            #îkeukenprofile=keukenprofile.append({'hour':'18:00:00','value':0.4},ignore_index=True)
            #keukenprofile=keukenprofile.append({'hour':'18:10:00','value':0.67},ignore_index=True)
            #keukenprofile=keukenprofile.append({'hour':'18:20:00','value':1.0},ignore_index=True)
            #keukenprofile=keukenprofile.append({'hour':'18:30:00','value':0.0},ignore_index=True)

            keukenprofile = pd.concat([keukenprofile,pd.DataFrame.from_records([{'hour':'18:00:00','value':0.40}])],ignore_index=True)
            keukenprofile = pd.concat([keukenprofile,pd.DataFrame.from_records([{'hour':'18:10:00','value':0.67}])],ignore_index=True)
            keukenprofile = pd.concat([keukenprofile,pd.DataFrame.from_records([{'hour':'18:20:00','value':1.00}])],ignore_index=True)
            keukenprofile = pd.concat([keukenprofile,pd.DataFrame.from_records([{'hour':'18:30:00','value':0.00}])],ignore_index=True)


        #keukenprofile=keukenprofile.append({'hour':'24:00:00','value':0.0},ignore_index=True)
        keukenprofile = pd.concat([keukenprofile,pd.DataFrame.from_records([{'hour':'24:00:00','value':0.0}])],ignore_index=True)

        #print(keukenprofile)
            
        dayschedules.addSchedule('Keuken_'+str(localcounter),'Kitchen profile for occupancy profiles '+str(group),keukenprofile)  
        keuken_day_profile_id=dayschedules.getLastId()
        keuken_profile_dict[group]=keuken_day_profile_id

        localcounter+=1
            
    
    ###################################################
    # Creating douche and kitchen sources with profiles
    ###################################################
    
    douche_week_profile=[ douche_profile_dict[tuple(g)] for g in schedules_groups]   #this is the week profile for douches, computed on basis on the week profiles of the occupants   
    weekschedules.addSchedule('Douche_Week','Douche week schedule based on occupants schedules',douche_week_profile)
    douche_week_schedule_ID=weekschedules.getLastId()
    
    sourceElemID=sourceElems.getSourceID('H2O_Badkamer')
    sourceController=controls.addSourceLimiter('Badkamer',douche_week_schedule_ID)
    
    #sources.addSource(bathroomid,sourceElemID,douche_week_schedule_ID,0,1.0) #direct control by schedule
    sources.addSource(bathroomid,sourceElemID,0,sourceController,1.0) #control via control var with limiter (stop source if RH>100)
    

    #Kitche week proifiles and adding sources in the model
    keuken_week_profile=[ keuken_profile_dict[tuple(g)] for g in schedules_groups]   #this is the week profile for keuken, computed on basis on the week profiles of the occupants
    weekschedules.addSchedule('Keuken_Week','Keuken week schedule based on occupants schedules',keuken_week_profile)
    keuken_week_schedule_ID=weekschedules.getLastId()

    sourceElemID=sourceElems.getSourceID('H2O_Keuken')
    KsourceController=controls.addSourceLimiter(zones.df.loc[keukenid,'name'],keuken_week_schedule_ID)

    #sources.addSource(keukenid,sourceElemID,keuken_week_schedule_ID,0,1.0)
    sources.addSource(keukenid,sourceElemID,0,KsourceController,1.0)
   

    #Laundry/Wasplaats
    
    laundryprofile=pd.DataFrame(columns=['hour','value'])
    
    
    '''laundryprofile=laundryprofile.append({'hour':'00:00:00','value':0},ignore_index=True)
    laundryprofile=laundryprofile.append({'hour':'08:00:00','value':1},ignore_index=True)
    laundryprofile=laundryprofile.append({'hour':'20:00:00','value':0},ignore_index=True)
    laundryprofile=laundryprofile.append({'hour':'24:00:00','value':0},ignore_index=True)'''
    
    laundryprofile = pd.concat([laundryprofile,pd.DataFrame.from_records([{'hour':'00:00:00','value':0}])])
    laundryprofile = pd.concat([laundryprofile,pd.DataFrame.from_records([{'hour':'08:00:00','value':1}])])
    laundryprofile = pd.concat([laundryprofile,pd.DataFrame.from_records([{'hour':'20:00:00','value':0}])])
    laundryprofile = pd.concat([laundryprofile,pd.DataFrame.from_records([{'hour':'24:00:00','value':0}])])

    laundryprofile.index = [1,2,3,4]
    
    dayschedules.addSchedule('Wasplaats','Day laundry profile',laundryprofile)  

    laundrydayprofile=dayschedules.getLastId()
    weekschedules.addSchedule('Laundry_Week','Laundry profile week',[ laundrydayprofile for i in range(12) ])
    laundryweekschedule=weekschedules.getLastId()
    LaundrySourceElemID=sourceElems.getSourceID('H2O_Wasplaats')
    
    if ('Wasplaats' in list(zones.df['name'])):
        laundryid=contam_functions.getzoneid('Wasplaats',zones.df)
    else:
        laundryid=bathroomid
        
    #sources.addSource(laundryid,LaundrySourceElemID,laundryweekschedule,0,1.0)
    WsourceController=controls.addSourceLimiter(zones.df.loc[laundryid,'name'],laundryweekschedule)
    sources.addSource(laundryid,LaundrySourceElemID,0,WsourceController,1.0)


    ############
    # Buffering
    ############
    
    #buffering in wet spaces
    # Medium buffering: wanden en plafond
    # Plafond --> vloer oppervlakte --> Volume / 3.0
    # Wanden: laten we een vierkant beschouwen :  perimeter = 4*sqrt(vloer oppervlakte) --> wanden oppervlakte = perimeter * 3
    # Wanden oppervlakte:  3*4*sqrt(vloer oppervlakte)
    # Total oppervlakte =   (vloer oppervlakte)*12*sqrt(vloer oppevlakte)
    
    bufferSourceId=sourceElems.getSourceID('Buffer_H2O')
    
    bufferspacesid=set([keukenid,laundryid,bathroomid]) #using set --> remove potential duplicates if laundry is in bathroom
    
    for spaceid in bufferspacesid:
    
        A=float(zones.df.loc[spaceid,'Vol'])/3.0
        multiplier=A+12*np.sqrt(A)
    
        sources.addSource(spaceid,bufferSourceId,0,0,multiplier,0.007) #last parameter: initial concentration (optional). 7g/kg = 50pc RH at 20degC





def addPollutantSourcePerFloorArea(contamModel,contaminantName,rate,unit):
    
    sourceElems=contamModel['sourceelems']
    sources=contamModel['sources']
    zones=contamModel['zones']

    sourceElems.addConstantRateSourceElement(contaminantName,'ccf',contaminantName+"S",'constant source',rate,unit)
    sourceElementID = sourceElems.nsources

    for spaceid in list(zones.df.index):

        A=float(zones.df.loc[spaceid,'Vol'])/3.0
        multiplier=A
        sources.addSource(spaceid,sourceElementID,0,0,multiplier,0) 


    
def addPollutantSourcePerTotalArea(contamModel,contaminantName,rate,unit):
    
    sourceElems=contamModel['sourceelems']
    sources=contamModel['sources']
    zones=contamModel['zones']

    sourceElems.addConstantRateSourceElement(contaminantName,'ccf',contaminantName+"S",'constant source',rate,unit)
    sourceElementID = sourceElems.nsources

    for spaceid in list(zones.df.index):

        A=float(zones.df.loc[spaceid,'Vol'])/3.0
        multiplier=A+12*np.sqrt(A)
        sources.addSource(spaceid,sourceElementID,0,0,multiplier,0) 
    
    
    
    

    



def read_standard_occupancy_file(csvf):
    
    f=open(csvf,'r')
    lines=f.read().split('\n')
    nlines=len(lines)

    df=pd.DataFrame(columns=['hour','zonename'])

    for i in range(nlines):

        if (i==0):
            name=lines[i]
            
        elif (i==1):
            description=lines[i]
            
        #elif(i<nlines-1):
        else:
            fields=lines[i].split(',')
            if (len(fields)>1):
                #df=df.append({'hour':fields[0],'zonename':fields[1],'douche':fields[2]=='douche'},ignore_index=True)
                df = pd.concat([df,pd.DataFrame.from_records([{'hour':fields[0],'zonename':fields[1],'douche':fields[2]=='douche'}])])

    df.index = range(1,len(df)+1)
            
    f.close()
         
    return name,description,df
    

