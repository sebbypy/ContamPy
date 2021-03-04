# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 11:09:50 2019

@author: spec
"""

import pandas as pd
import datetime
import os

class loadCONTAMWeather:
    
    def __init__(self):
        
        self.description="""Loader for CONTAM Weather files
        
A year has to be chosen in order to load the file as the CONTAM weather files only contain month and day

The current year is chosen by default (left field blank)"""
   
        self.parameters={
                'Year to assign':'string'
                }
    

    def execute(self,fname,p):
 

        if (p['Year to assign']==''):
            year=datetime.date.today().year
        else:
            year=int(p['Year to assign'])
        
        
        f=open(fname,'r')
        FoundStartLine=False
    
        line=True
    
        count=0
        while line:
            line=f.readline()
            count+=1
            
            if ('!Date' in line and 'Time' in line):
                FoundStartLine=True
                f.close()
                break
    
        if (not FoundStartLine):
            return pd.DataFrame()
        
        df=pd.read_csv(fname,skiprows=count-1,delimiter='\t')
    
        newtime=[]
    
        for date,time in zip(df['!Date'],df['Time']):
    
            mm,dd=date.split('/')
            HH,MM,SS=time.split(':')
    
            flag=False
            if(HH=='24'):
                HH='23'
                flag=True
            
            newtime.append(datetime.datetime(year,int(mm),int(dd),int(HH),int(MM),int(SS)))
    
            if flag:
                newtime[-1]=newtime[-1]+datetime.timedelta(hours=1)
    
                           
        df.index=newtime
        df=df.drop(['!Date','Time'],axis=1)
        
        df=df[df.index.year==year]
    
        
        return(df)
        

class ExportCONTAMW:
    
    def __init__(self):
        
        self.description="""Exporter for CONTAM Weather files.
        
If the weather file is longer than one year, it will exported in multiple files with a year suffix"""
                
                
        # fields that are required in the dataframe
        self.required_fields={
                'Temperature':'External temperature [K]',
                'Absolute Humidity': 'Absolute Humidity [gr/kg]',
                'Wind Direction':'Wind direction from N, clockwise [degrees]',
                'Wind Speed':'Wind Velocity [m/s]'
                }   


    def execute(self,df,fullname,description):
 
        ok=True
    
        # required fields: Temperature, WindDirection, WindVelocity, AbsHum
  
    
        #requiredFields=['Temperature','Absolute Humidity','Wind Direction','WindVelocity']
    
    
        for rf in self.required_fields.keys():
            if rf not in df.columns:
                Message='Field '+rf+' is not in the data frame but is required to export a CONTAM file'
                Message+='\nExport canceled'
                ok=False
                return(ok,Message)
    

        #drop NAN
        df.dropna(inplace=True)

        df.drop(df.index[ (df.index.month==2) & (df.index.day==29)],inplace=True)

        startyear=df.index[0].date().year
        endyear=df.index[-1].date().year

        if (startyear==endyear):
            self.writeoneyear(df,fullname,description)

        else:
            for y in range(startyear,endyear+1):
                
                yeardf=df[df.index.year==y]
                
                self.writeoneyear(yeardf,fullname.replace('.wth','-'+str(y)+'.wth'),description+' -'+str(y))
        
        Message='Export succeeded'
        ok=True
        
        return(ok,Message)



    def writeoneyear(self,df,fullname,description):
    
        startdate=df.index[0].date()
        enddate=df.index[-1].date()
        
        print(startdate,enddate)
        print(fullname)
        
        Tground=283.15
        
        #fullname=os.path.join(path,fname)
        
        f=open(fullname,'w')
        
        f.write('WeatherFile ContamW 2.0 \n')
        f.write(description+'- GENERATED USING BBRI PYTHON GUI\n')
    
        f.write(str(startdate.month)+'/'+str(startdate.day)+' ! start-of-file date\n')
        f.write(str(enddate.month)+'/'+str(enddate.day)+' ! start-of-file date\n')
    
        f.write('!Date	DofW	Dtype	DST	Tgrnd [K]\n')
        
        for date in pd.date_range(startdate,enddate,freq='1D'):
            
            if (date.month==2 and date.day==29):
                continue
            
            m=str(date.month)
            d=str(date.day)
            
            DayType=date.weekday()+1  # day types in CONTAM start at 1 for Monday
            DayOfWeek=DayType-1       # day of week in CONTAM are 1-7 from Sunday to Saturday
            if (DayOfWeek==0): DayOfWeek=7 # Sundy is 1
            
            f.write(m+'/'+d+'\t'+str(DayOfWeek)+'\t'+str(DayType)+'\t'+'0'+'\t'+str(Tground)+'\n')
    
        #
        f.write('!Date	Time	Ta [K]	Pb [Pa]	Ws [m/s]	Wd [deg]	Hr [g/kg]	Ith [kJ/m^2]	Idn [kJ/m^2]	Ts [K]	Rn [-]	Sn [-]\n')
        
        for index in df.index:
            f.write(str(index.month)+'/'+str(index.day)+'\t')
            f.write(index.time().isoformat()+'\t')
            f.write(str(df.loc[index,'Temperature'])+'\t')
            f.write(str(101325)+'\t')
            f.write(str(df.loc[index,'Wind Speed'])+'\t')
            f.write(str(df.loc[index,'Wind Direction'])+'\t')
            f.write(str(df.loc[index,'Absolute Humidity'])+'\t')
            f.write(str(0)+'\t') # Ith
            f.write(str(0)+'\t') # Idn
            f.write(str(273.15)+'\t') # Ts
            f.write(str(0)+'\t') #Rn
            f.write(str(1)+'\n') #Sn
            
        # si le df s arrete a 23h, il y a des chances que la simu CONTAM aille jusque 24...
        if(index.time().hour==23):
            f.write(str(index.month)+'/'+str(index.day)+'\t')
            f.write('24:00:00\t')
            f.write(str(df.loc[index,'Temperature'])+'\t')
            f.write(str(101325)+'\t')
            f.write(str(df.loc[index,'Wind Speed'])+'\t')
            f.write(str(df.loc[index,'Wind Direction'])+'\t')
            f.write(str(df.loc[index,'Absolute Humidity'])+'\t')
            f.write(str(0)+'\t') # Ith
            f.write(str(0)+'\t') # Idn
            f.write(str(273.15)+'\t') # Ts
            f.write(str(0)+'\t') #Rn
            f.write(str(1)+'\n') #Sn
            
            
    
    
    
        f.close()
    



class ExportCONTAMCTM:

#    SpeciesFile ContamW 2.0 ! file and version identification		
#    H2OCTM  ! species file description		
#    1/1  ! day of year (1/1  12/31)		
#    12/31  ! day of year (1/1  12/31)		
#    1      ! number of species		
#    H2O ! name of species 1 (16 characters max)		
#    !date	Time	H2O (kg/kg)
#    
    
    
    def __init__(self):
        
        self.description="""Exporter for CONTAM contaminant file.

For now only exports H2O, could be extended in the future. Supposes absolue humidity is in gr/kg (and will be exported in kg/kg)

If the weather file is longer than one year, it will exported in multiple files with a year suffix"""
                
                
        # fields that are required in the dataframe
        self.required_fields={
                'Absolute Humidity': 'Absolute Humidity [gr/kg]',
            }   


    def execute(self,df,fullname,description):
 
        ok=True
    
        for rf in self.required_fields.keys():
            if rf not in df.columns:
                Message='Field '+rf+' is not in the data frame but is required to export a CONTAM file'
                Message+='\nExport canceled'
                ok=False
                return(ok,Message)
    

        #drop NAN
        df.dropna(inplace=True)

        df.drop(df.index[ (df.index.month==2) & (df.index.day==29)],inplace=True)

        startyear=df.index[0].date().year
        endyear=df.index[-1].date().year

        if (startyear==endyear):
            self.writeoneyear(df,fullname,description)

        else:
            for y in range(startyear,endyear+1):
                
                yeardf=df[df.index.year==y]
                
                self.writeoneyear(yeardf,fullname.replace('.wth','-'+str(y)+'.wth'),description+' -'+str(y))
        
        Message='Export succeeded'
        ok=True
        
        return(ok,Message)



    def writeoneyear(self,df,fullname,description):
    
        startdate=df.index[0].date()
        enddate=df.index[-1].date()
        
        
        f=open(fullname,'w')
        
        f.write('SpeciesFile ContamW 2.0 ! file and version identification\n')
        f.write(description+' - GENERATED USING PYTHON GUI ! species file description\n')
    
        f.write(str(startdate.month)+'/'+str(startdate.day)+' ! start-of-file date\n')
        f.write(str(enddate.month)+'/'+str(enddate.day)+' ! end-of-file date\n')
    
        f.write('1 ! number of species\n')
        f.write('H2O ! name of species 1 (16 characters max)\n')
        f.write('!date	Time	H2O (kg/kg)\n')
            
        #
        
        for index in df.index:
            f.write(str(index.month)+'/'+str(index.day)+'\t')
            f.write(index.time().isoformat()+'\t')
            f.write(str(df.loc[index,'Absolute Humidity']/1000)+'\n')
            
        # si le df s arrete a 23h, il y a des chances que la simu CONTAM aille jusque 24...
        if(index.time().hour==23):
            f.write(str(index.month)+'/'+str(index.day)+'\t')
            f.write('24:00:00\t')
            f.write(str(df.loc[index,'Absolute Humidity']/1000)+'\n')
            
    
    
        f.close()
    
    

class writeCVF:
    
    def __init__(self):
        
        self.description="None"

    
    def execute(self,df,fullname,p):
        
        df=pd.DataFrame(df)
        
        
        startdate=df.index[0].date()
        enddate=df.index[-1].date()
    

        date=[str(index.month)+'/'+str(index.day) for index in df.index]
        hour=[index.time().isoformat() for index in df.index]
    
        
        cols=['date','hour']+list(df.columns)
        df['date']=date
        df['hour']=hour

        df=df[cols]

        if df['hour'].iloc[-1]=='23:00:00':
            df.loc[df.index[-1]+datetime.timedelta(hours=1),:]=df.loc[df.index[-1],:]
            df['hour'].iloc[-1]='24:00:00'

        f=open(fullname,'w')
        
        f.write('ContinuousValuesFile ContamW 2.1\n')
        f.write('CVF file generated by Python\n')
        f.write(df['date'].iloc[0]+" "+df['date'].iloc[-1]+'\n')
        f.write(str(len(df.columns)-2)+'\n')
        
        for c in df.drop(['date','hour'],axis=1).columns:
            f.write(str(c)+'\n')
            
        df.to_csv(f,sep='\t',header=False,index=False)



        f.close()

    
    
    
    
    
class loadCONTAMlog:
    
    def __init__(self):
        
        self.description="""Loader for CONTAM log files

A year has to be chosen in order to load the file as the CONTAM files only contain month and day.The current year is chosen by default (left field blank)

The filters are regular expression such as  Q_* or *CO2*. This allow to keep only interesting fields. They should be separated by a semicol  (e.g.  "Q_*;CO2_*;*_SP*_" )

"""
   
        self.parameters={
                'Year to assign':'string',
                'Filters':'string',
                'Load ach file?':'checkbox',
                }
    

    def execute(self,fname,p):
 

        if (p['Year to assign']==''):
            year=datetime.date.today().year
        else:
            year=int(p['Year to assign'])
        
        filters = p['Filters'].split(';')
        
        df=pd.read_csv(fname,skiprows=2,delimiter='\t')
        
        f=open(fname,'r')
        headers=f.readline().replace('\n','').split('\t')
        headers=headers[3:]

        f.close()
        
        headers.insert(0,'Date')
        headers.insert(1,'Time')
        headers.insert(2,'Seconds')
    
        df.columns=headers
        newtime=[]

    
        for date,time in zip(df['Date'],df['Time']):
    
            mm,dd=date.split('/')
            HH,MM,SS=time.split(':')
    
            flag=False
            if(HH=='24'):
                HH='23'
                flag=True
            
            newtime.append(datetime.datetime(year,int(mm),int(dd),int(HH),int(MM),int(SS)))
    
            if flag:
                newtime[-1]=newtime[-1]+datetime.timedelta(hours=1)
    
    
    
        df.index=pd.to_datetime(newtime)
        
        df=df.drop(['Date','Time','Seconds'],axis=1)
        
       
        
        df=df[df.index.year==year]


        newdf=pd.DataFrame()
    
        if (filters[0] != ''):

            #filtering the data
            for f in filters:
                
                newdf=pd.concat([newdf,df.filter(regex=f)],axis=1)
            
        else:
            newdf=df            

        if (p['Load ach file?']==True):
            ach=readCONTAMAch(fname.replace('.log','.ach'),year)            
            newdf['Total air flow']=ach['Total air flow']
        
        return(newdf)
        
    
def readCONTAMAch(fname,year):

    f=open(fname,'r')
    volume=f.readline().split()[-1]
    volume=float(volume)
    f.close()
    
    df=pd.read_csv(fname,skiprows=1,delimiter='\t')
    
    newtime=[]

    for date,time in zip(df['day'],df['time']):
    
        mm,dd=date.split('/')
        HH,MM,SS=time.split(':')

        flag=False
        if(HH=='24'):
            HH='23'
            flag=True
        
        newtime.append(datetime.datetime(year,int(mm),int(dd),int(HH),int(MM),int(SS)))

        if flag:
            newtime[-1]=newtime[-1]+datetime.timedelta(hours=1)
    
        
    df.index=newtime
    df=df.drop(['day','time','path','duct'],axis=1)
    
    df=df[df.index.year==year]

    df['total']=df['total']*volume
    df.rename(columns={'total':'Total air flow'},inplace=True)    

    return(df)




