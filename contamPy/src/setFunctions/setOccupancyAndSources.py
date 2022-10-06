
import contam_functions
import pandas as pd
import numpy as np
import datetime

import os

def apply(contam_data,occupancyProfileName,profilesDir,CO2Rate=16,H2ORate=55,CO2Sleeping=0.625,H2OSleeping=0.7):
    """Assumptions:
        There are one more occupants than bedrooms"""


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


    

    if contam_data['zones'].getNumberOfZones() == 1 :
        print("Only a single zone in the model, skipping occupancy and sources definition")
        return 


    numberOfBedrooms = zones.getNumberOfBedrooms()
    numberOfOccupants = numberOfBedrooms+1

    occupantsReferenceSchedules,co2EmissionsReferenceSchedules,h2oEmissionsReferenceSchedules = generateOccupantsDaySchedules(numberOfOccupants,
                                                                                                                              profilesDir,
                                                                                                                              zones,
                                                                                                                              contam_data,
                                                                                                                              oschedules,
                                                                                                                              dayschedules)

    occupantsReferenceWeekSchedules,occupantCO2WeekSchedule,occupantH2OWeekSchedule = generateOccupantsWeekSchedules(numberOfOccupants,
                                                                                                                     occupancyProfileName,
                                                                                                                     occupantsReferenceSchedules,
                                                                                                                     co2EmissionsReferenceSchedules,
                                                                                                                     h2oEmissionsReferenceSchedules,
                                                                                                                     weekschedules)


    for oid in range(1,numberOfOccupants+1):
        
        exposures.addExposure('O'+str(oid)+' Exposure',
                                occupantsReferenceWeekSchedules[oid],
                                [
                                {'name':'CO2','schedule':occupantCO2WeekSchedule[oid],'rate':CO2Rate,'unit':'L/h','value_file':0},
                                {'name':'H2O','schedule':occupantH2OWeekSchedule[oid],'rate':H2ORate,'unit':'g/h','value_file':0}
                                ]
                            )
        
        controls.addexposuresensor(oid,'CO2')
        controls.addexposuresensor(oid,'VOC')

        
 
    schedules_groups,unique_groups = getDaySchedulesCombinations(exposures)
    #schedule groups = combinsations of occupants schedules for all 12 refernce days
    #unique_groups = unique combinations 
            
    bathroomid = zones.getBathroomID()
    bathroomName = zones.getBathroomName()

    shower_profile_dict = generateDailyShowerProfiles(unique_groups,oschedules,bathroomid,dayschedules)    
    shower_week_profile=[ shower_profile_dict[tuple(g)] for g in schedules_groups]   #this is the week profile for showers, computed on basis on the week profiles of the occupants   
    weekschedules.addSchedule('Shower_Week','Shower week schedule based on occupants schedules',shower_week_profile)
    shower_week_schedule_ID=weekschedules.getLastId()    
    sourceElemID=sourceElems.getSourceID('H2O_Badkamer')
    sourceController=controls.addSourceLimiter(bathroomName,shower_week_schedule_ID)    
    sources.addSource(bathroomid,sourceElemID,0,sourceController,1.0) #control via control var with limiter (stop source if RH>100)
    

    kitchenid = zones.getKitchenID()
    kitchenName = zones.getKitchenName()

    kitchen_profile_dict = generateDailyKitchenProfiles(unique_groups,oschedules,kitchenid,dayschedules)

    kitchen_week_profile=[ kitchen_profile_dict[tuple(g)] for g in schedules_groups]   #this is the week profile for kitchen, computed on basis on the week profiles of the occupants
    weekschedules.addSchedule('Kitchen_Week','Kitchen week schedule based on occupants schedules',kitchen_week_profile)
    kitchen_week_schedule_ID=weekschedules.getLastId()
    sourceElemID=sourceElems.getSourceID('H2O_Keuken')
    KsourceController=controls.addSourceLimiter(kitchenName,kitchen_week_schedule_ID)
    sources.addSource(kitchenid,sourceElemID,0,KsourceController,1.0)
   

    laundrydayprofile = generateLaundrySourceProfile(dayschedules)
    weekschedules.addSchedule('Laundry_Week','Laundry profile week',[ laundrydayprofile for i in range(12) ])
    laundryweekschedule=weekschedules.getLastId()
    LaundrySourceElemID=sourceElems.getSourceID('H2O_Wasplaats')

    laundryid = zones.getLaundryID()    
    laundryName = zones.getLaundryName()

    #sources.addSource(laundryid,LaundrySourceElemID,laundryweekschedule,0,1.0)

    WsourceController=controls.addSourceLimiter(laundryName,laundryweekschedule)
    sources.addSource(laundryid,LaundrySourceElemID,0,WsourceController,1.0)


    addH2OBuffering(zones, sources, sourceElems, kitchenid, laundryid, bathroomid)




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
                #df=df.append({'hour':fields[0],'zonename':fields[1],'shower':fields[2]=='shower'},ignore_index=True)
                df = pd.concat([df,pd.DataFrame.from_records([{'hour':fields[0],'zonename':fields[1],'shower':fields[2]=='shower'}])])

    df.index = range(1,len(df)+1)
            
    f.close()
         
    return name,description,df
    

def generateOccupantsDaySchedules(numberOfOccupants,profilesDir,zones,contam_data,oschedules,dayschedules):
    
    occupantsReferenceSchedules={} #day occupancy schedules day dictionnary text_key:id
    
    co2EmissionsReferenceSchedules={} # occupancy schedule id : CO2 schedule id
    h2oEmissionsReferenceSchedules={} # occupancy schedule id:  H2O schedule id
    
  
    bedrooms = zones.getAllBedroomsNames(sortingMethod='Volume')
    biggestbedroom=bedrooms[0]
    bedrooms.remove(biggestbedroom)

    
    for oid in range(1,numberOfOccupants+1):
        
        for ptype in ['Home','Busy','Away']:

            fname=os.path.join(profilesDir,'profile_Occupant'+str(oid)+'_'+ptype+'.csv')
        
            if (not os.path.exists(fname)):
                #print(fname+" does not exist, skipping")
                continue
        
            name,des,df=read_standard_occupancy_file(fname)


            if (oid <3):
                bedroomName=biggestbedroom

            elif (oid>2):
                bedroomName=bedrooms[oid-3]
                

            df.replace('Bedroom',bedroomName,inplace=True)
            df.replace('Kitchen',zones.getKitchenName(),inplace=True)
            df.replace('WC',zones.getToiletName(),inplace=True)
            df.replace('Livingroom',zones.getLivingroomName(),inplace=True)
            df.replace('Bathroom',zones.getBathroomName(),inplace=True)


            df['zid']=zones.getZonesID(df['zonename'])
            

            # add day occupancy schedule for occupant
            oschedules.addSchedule(name,des,df)
            scheduleid=oschedules.getLastId()
            
            occupantsReferenceSchedules['O'+str(oid)+'_'+ptype]=scheduleid

            bedroomID = zones.getZonesID([bedroomName])[0]
            
            co2schedule=oschedules.genEmissionSchedule(scheduleid,bedroomID,0.625)
            dayschedules.addSchedule('CO2_Day_O'+str(oid)+'S'+str(scheduleid),'CO2 emission for occ-profile '+str(scheduleid),co2schedule)

            co2EmissionsReferenceSchedules[scheduleid]=dayschedules.getLastId()

            h2oschedule=oschedules.genEmissionSchedule(scheduleid,bedroomID,0.7)
            dayschedules.addSchedule('H2O_Day_O'+str(oid)+'S'+str(scheduleid),'H2O emission for occ-profile '+str(scheduleid),h2oschedule)

            h2oEmissionsReferenceSchedules[scheduleid]=dayschedules.getLastId()
            
            
            
    return occupantsReferenceSchedules,co2EmissionsReferenceSchedules,h2oEmissionsReferenceSchedules


def generateOccupantsWeekSchedules(numberOfOccupants,occupancyProfileName,occupantsReferenceSchedules,co2EmissionsReferenceSchedules,h2oEmissionsReferenceSchedules,weekschedules):
    
    occupantCO2WeekSchedule = {}
    occupantH2OWeekSchedule = {}
    occupantsReferenceWeekSchedules = {}
    
    
    for oid in range(1,numberOfOccupants+1):
    
        #this should be an input parameter or deduced from a input parameter
        
        if (occupancyProfileName=='default-home'):
        
            textschedulelist= [ 'O'+str(oid)+'_'+'Home' for i in range(12) ] #full text list of 12 day schedules 
        
        elif (occupancyProfileName=='default-active'):
        
            textschedulelist= [ 'O'+str(oid)+'_'+'Home' if i in [0,6] else 'O'+str(oid)+'_Busy' for i in range(12) ] #full text list of 12 day schedules 
        
        else:
            raise ValueError("Wrong occupancy profile",occupancyProfileName)

        
        occupantsReferenceWeekSchedules[oid]=[ occupantsReferenceSchedules[x] for x in textschedulelist]            # list of 12 schedules with ids

        co2weekschedule=[co2EmissionsReferenceSchedules[x] for x in occupantsReferenceWeekSchedules[oid]]
        h2oweekschedule=[h2oEmissionsReferenceSchedules[x] for x in occupantsReferenceWeekSchedules[oid]]
       
        weekschedules.addSchedule('CO2W_O'+str(oid),'CO2 Week schedule for occupant '+str(oid),co2weekschedule)
        co2Wid=weekschedules.getLastId()
               
        
        weekschedules.addSchedule('H2OW_O'+str(oid),'H2O Week schedule for occupant '+str(oid),h2oweekschedule)
        h2oWid=weekschedules.getLastId()


        occupantCO2WeekSchedule[oid]=co2Wid
        occupantH2OWeekSchedule[oid]=h2oWid

    

    return occupantsReferenceWeekSchedules,occupantCO2WeekSchedule,occupantH2OWeekSchedule


def generateDailyShowerProfiles(unique_groups,oschedules,bathroomid,dayschedules):
        
    # Implementation details:
    # for each occupant, the moment of the shower is specified in the generic CSV files
    # creating a "shower" schedule that cumulates the shower of all occupants    
    
    shower_profile_dict={}

    localcounter=1

    for group in unique_groups:
        showerprofile=pd.DataFrame()

        for profileid in group: #individual occupancy profile        
 
           moddf=oschedules.schedules[profileid]['dataframe'].copy()
           moddf.index=moddf['hour']
           moddf.drop(['24:00:00'],inplace=True)
           moddf.index=pd.to_datetime(moddf.index)

           
           showertime=moddf[ (moddf['zid']==bathroomid) & (moddf['shower']==1.0) ].index

           if (len(showertime)>0):
                for t in showertime:
                    #shower 10  min for each individual
                    locprofile=pd.DataFrame(index=[t,t+datetime.timedelta(minutes=10)],columns=[profileid])
                    locprofile.loc[t,profileid]=1.0
                    locprofile.loc[t+datetime.timedelta(minutes=10),profileid]=0.0
                    
                    #adding one column for each indidividual
                    showerprofile=pd.concat([showerprofile,locprofile],axis=1)


        showerprofile.fillna(value=0)
        showerprofile=showerprofile.sum(axis=1) #sum of all indidviduals to have a single profile
        showerprofile.index=[ str(x.time()) for x in showerprofile.index ] #going back to CONTAM compatible time format
        showerprofile.loc['00:00:00']=0
        showerprofile.loc['24:00:00']=0
        showerprofile.name='value'
        showerprofile.sort_index(inplace=True)
        showerprofile=pd.DataFrame(showerprofile)
        showerprofile.loc[:,'hour']=showerprofile.index
        dayschedules.addSchedule('ShowerDay_'+str(localcounter),'Day shower profile for occupancy profiles '+str(group),showerprofile)  
        contam_day_profile_id=dayschedules.getLastId()
        shower_profile_dict[group]=contam_day_profile_id
        
        
    return shower_profile_dict






def generateDailyKitchenProfiles(unique_groups,oschedules,kitchenid,dayschedules):
    """Generate H2O source profiles in the kitchen (morning,noon,evening)
    depending if there are present occupants or not"""
        
    """Water production time are not exactly synchroneous with occupancy
    e.g. For noon, water production is always at 12:00, but we only activate it
    if there is some occupancy in the kitchen in the period 12:00-14:00
    Rationale is similar for other meals"""
    
    kitchen_profile_dict={}
    
    localcounter=1    
    for group in unique_groups:

        kitchenprofile=pd.DataFrame(columns=['hour','value'])
        kitchenocc=pd.DataFrame()

        for profileid in group:
            
            moddf=oschedules.schedules[profileid]['dataframe'].copy()
            moddf.index=moddf['hour']
            moddf.drop(['24:00:00'],inplace=True)
            moddf.index=pd.to_datetime(moddf.index)

            kitchenpres= (moddf['zid']==kitchenid)
            kitchenpres.name=profileid
            kitchenocc=pd.concat([kitchenocc,kitchenpres],axis=1) #1 column per occupant

        kitchenocc=kitchenocc.sum(axis=1)

        kitchenprofile = pd.concat([kitchenprofile,pd.DataFrame.from_records([{'hour':'00:00:00','value':0}])],ignore_index=True)

        
        #morning
        boolindex=( (kitchenocc.index.time > datetime.time(6)) & (kitchenocc.index.time < datetime.time(9)) )
        if (kitchenocc.loc[boolindex].max() > 0 ): #occupation durant la periode
            kitchenprofile = pd.concat([kitchenprofile,pd.DataFrame.from_records([{'hour':'07:00:00','value':0.4}])],ignore_index=True)
            kitchenprofile = pd.concat([kitchenprofile,pd.DataFrame.from_records([{'hour':'07:10:00','value':0.0}])],ignore_index=True)


        #noon
        boolindex=( (kitchenocc.index.time >= datetime.time(12)) & (kitchenocc.index.time < datetime.time(14)) )
        if (kitchenocc.loc[boolindex].max() > 0 ): #occupation durant la periode
            kitchenprofile = pd.concat([kitchenprofile,pd.DataFrame.from_records([{'hour':'12:00:00','value':0.4}])],ignore_index=True)
            kitchenprofile = pd.concat([kitchenprofile,pd.DataFrame.from_records([{'hour':'12:10:00','value':0}])],ignore_index=True)


        #evenint
        boolindex=( (kitchenocc.index.time >= datetime.time(18)) & (kitchenocc.index.time < datetime.time(20)) )
        if (kitchenocc.loc[boolindex].max() > 0 ): #occupation durant la periode

            kitchenprofile = pd.concat([kitchenprofile,pd.DataFrame.from_records([{'hour':'18:00:00','value':0.40}])],ignore_index=True)
            kitchenprofile = pd.concat([kitchenprofile,pd.DataFrame.from_records([{'hour':'18:10:00','value':0.67}])],ignore_index=True)
            kitchenprofile = pd.concat([kitchenprofile,pd.DataFrame.from_records([{'hour':'18:20:00','value':1.00}])],ignore_index=True)
            kitchenprofile = pd.concat([kitchenprofile,pd.DataFrame.from_records([{'hour':'18:30:00','value':0.00}])],ignore_index=True)


        kitchenprofile = pd.concat([kitchenprofile,pd.DataFrame.from_records([{'hour':'24:00:00','value':0.0}])],ignore_index=True)

            
        dayschedules.addSchedule('Kitchen_'+str(localcounter),'Kitchen profile for occupancy profiles '+str(group),kitchenprofile)  
        kitchen_day_profile_id=dayschedules.getLastId()
        kitchen_profile_dict[group]=kitchen_day_profile_id

        localcounter+=1
        
        
    return kitchen_profile_dict



def getDaySchedulesCombinations(exposures):
    """return combinations of occupant day profiles + a list of unique combinations"""
        
    schedules_groups=[]

    for daytype in range(12):

        daylist=[]
        schedules_groups.append(daylist)  #cumulated day_profiles

        for oid,v in exposures.exposures.items():
            daylist.append(v['day_schedules'][daytype])
            
    # daylist combination of occupants profiles for each day tpe
    
    unique_groups=set(tuple(row) for row in schedules_groups) 
    #unique combination of dayly profiles
    #In most cases: there is one combination for weenkend, and one combination for weedays
    
    
    return schedules_groups,unique_groups


def generateLaundrySourceProfile(dayschedules):
    
    laundryprofile=pd.DataFrame(columns=['hour','value'])   
    laundryprofile = pd.concat([laundryprofile,pd.DataFrame.from_records([{'hour':'00:00:00','value':0}])])
    laundryprofile = pd.concat([laundryprofile,pd.DataFrame.from_records([{'hour':'08:00:00','value':1}])])
    laundryprofile = pd.concat([laundryprofile,pd.DataFrame.from_records([{'hour':'20:00:00','value':0}])])
    laundryprofile = pd.concat([laundryprofile,pd.DataFrame.from_records([{'hour':'24:00:00','value':0}])])

    laundryprofile.index = [1,2,3,4]
    
    dayschedules.addSchedule('Laundry','Day laundry profile',laundryprofile)  

    laundrydayprofile=dayschedules.getLastId()
    
    return laundrydayprofile
    


def addH2OBuffering(zones,sources,sourceElems,kitchenid,laundryid,bathroomid):
    """
    Adding moisture buffering in 'wet' spaces
    Estimates the wall and ceiling areas from volume
    Add corresponding source
    Source Element is already existing in the template
    """
    
    
    bufferSourceId=sourceElems.getSourceID('Buffer_H2O')
    
    bufferspacesid=set([kitchenid,laundryid,bathroomid]) #using set --> remove potential duplicates if laundry is in bathroom
    
    for spaceid in bufferspacesid:
    
        A=float(zones.df.loc[spaceid,'Vol'])/3.0
        multiplier=A+12*np.sqrt(A)
    
        sources.addSource(spaceid,bufferSourceId,0,0,multiplier,0.007) #last parameter: initial concentration (optional). 7g/kg = 50pc RH at 20degC


