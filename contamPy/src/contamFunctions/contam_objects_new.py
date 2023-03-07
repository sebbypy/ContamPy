import pandas as pd
import numpy as np

pd.options.mode.chained_assignment = None

import os
dirPath = os.path.dirname(os.path.realpath(__file__))
import sys
sys.path.append(os.path.join(dirPath,'../utilities'))

from utilityFunctions import shortenTooLongName




class levels:

    # nr // level number (IX), in order from 1 to nlev
    # refht // reference elevation of level [m] (R4)
    # delht // delta elevation to next level [m] (R4) {W}
    # nicon // number of icons on this level (IX)
    # u_rfht // units of reference elevation (I2) {W}
    # u_dlht // units of delta elevation (I2) {W}
    # name[] // level name (I1)

    def __init__(self):
    
        self.headers=['nr','refht','delht','nicon','u_rfht','u_dlht','name']
        self.df = pd.DataFrame(columns=self.headers)
    
        self.icons={} #dictionnary of dataframes --> icons. 1 df per level
    
    def readCONTAMlevels(self,filereader,currentline):
    
        nlevels,self.comment=currentline.split('!')
        self.nlevels=int(nlevels)
        
        self.contamheader=filereader.readline() #headers
        mydict={}
            
        for n in range(self.nlevels):
            
            fields=filereader.readline().split()
            mydict={self.headers[i]:fields[i] for i in range(len(fields))}
    
            self.df = pd.concat([self.df,pd.DataFrame.from_records([mydict])])

            self.icons[mydict['nr']]=self.readlevelicons(filereader,mydict['nicon'])

        self.df.index=self.df['nr'].astype(int)
        self.df.drop(['nr'],axis=1,inplace=True)

        self.df=convert_cols(self.df)
        

 
    def readlevelicons(self,filereader,nicons):

        self.iconheader=filereader.readline() #ico header
        
        iconsdf=pd.DataFrame(columns=['icn','col','row','#'])
        
        for ico in range(int(nicons)):
            line=filereader.readline().replace('\r','')
            
            
            icn,col,row,elemid=line.split()
            iconsdf.loc[ico,'icn']=icn
            iconsdf.loc[ico,'col']=col
            iconsdf.loc[ico,'row']=row
            iconsdf.loc[ico,'#']=elemid
        
        iconsdf=convert_cols(iconsdf)
        
        return iconsdf
        
    def writeCONTAMlevels(self,g):

        g.write(str(self.nlevels)+' !'+self.comment)
        g.write(self.contamheader)

        
        for levelid in self.df.index:

            g.write(str(levelid)+' ')
            [g.write(str(self.df.loc[levelid,x])+' ') for x in self.df.columns]
            g.write('\n')
            self.writelevelicons(g,str(levelid))



            
    def writelevelicons(self,g,levelid):
        
        
        g.write(self.iconheader)
        self.icons[levelid].to_csv(g,mode='a',header=False,sep=' ',index=False,line_terminator='\n')



class zones:

    #expected zone info:
    # nr // zone number (IX); in order from 1 to _nzone
    # flags // zone flags – bits defined in contam.h (U2)
    # ps // week schedule index (IX); converted to pointer
    # pc // control node index (IX); converted to pointer
    # pk // kinetic reaction index (IX); converted to pointer
    # pl // building level index (IX); converted to pointer
    # relHt // zone height [m] (R4)
    # Vol // zone volume [m^3] (R4)
    # T0 // initial zone temperature [K] (R4)
    # P0 // initial zone pressure [Pa] (R4)
    # name[] // zone name (I1) {W}
    # color // zone fill color (I2) {W} {Contam 2.4}
    # u_Ht // units of height (I2) {W}
    # u_V // units of volume (I2) {W}
    # u_T // units of temperature (I2) {W}
    # u_P // units of pressure (I2) {W}
    # cdaxis // conv/diff axis – (0=no cd, 1-4 => cd axis direction) (I2)
    # vf_type // 0=no value file, 1=use cvf, 2=use dvf (I2) {CONTAM 3.2}
    # vf_node_name[NAMELEN] // value file node name (I1) {CONTAM 3.2}
    # cfd // cfd zone (0=no, 1=yes) (I2) {CONTAM 3.0}
    
    def __init__(self):
    
        self.headers=['nr','flags','ps','pc','pk','pl','relHt','Vol','T0','P0','name','color','u_Ht','u_V','u_T','u_P','cdaxis','vf_type','vf_node_name','cfd']
        self.df = pd.DataFrame(columns=self.headers)
    
    def readCONTAMzones(self,filereader,currentline):
        
        nzones,self.comment=currentline.split('!')
        self.nzones=int(nzones)
        self.contamheader=filereader.readline() #headers

        for n in range(self.nzones):
            fields=filereader.readline().split()
            
            minlen = min(len(fields),len(self.headers))
            
            mydict={self.headers[i]:fields[i] for i in range(minlen)}
    
            if mydict['vf_type']=='0':
                mydict['cfd']=mydict['vf_node_name']
                mydict['vf_node_name']=''

            
            

            self.df = pd.concat([self.df,pd.DataFrame.from_records([mydict])])

        self.df.index=self.df['nr'].astype(int)
        self.df.drop(['nr'],axis=1,inplace=True)

        self.df=convert_cols(self.df)


    def writeCONTAMzones(self,g):
        
        g.write(str(self.nzones)+' !'+self.comment)
        g.write(self.contamheader)
        self.df.to_csv(g,header=False,sep=' ',line_terminator='\n')


    def getZonesDataFrame(self):
        
        return self.df
    
    
    def replaceZonesDataFrame(self,newzonesdf):
        
        self.df = newzonesdf

    def getNumberOfZones(self):
        
        return self.nzones-2
    
    def getZonesNames(self):
        
        return list(self.df['name'])

    def getZonesID(self,zoneList):
        
        ids=[]
        
        for zonename in zoneList:
            if zonename != 'ext':            
                ids.append(self.df[self.df['name']==zonename].index[0])
            else:
                ids.append(-1)
        
        return ids

    def defineZonesFunctions(self,kitchenKey,bedroomsKey,laundryKey,bathroomKey,toiletKey,livingKey):
        
        self.kitchenKey = kitchenKey
        self.bedroomsKey = bedroomsKey
        self.laundryKey = laundryKey
        self.bathroomKey = bathroomKey
        self.toiletKey = toiletKey
        self.livingKey = livingKey
    
    def getLivingroomName(self):
        
        name = self.df[self.df['name'].str.contains(self.livingKey)]['name'].iloc[0]
        
        return name


    def getKitchenName(self):
        
        name = self.df[self.df['name'].str.contains(self.kitchenKey)]['name'].iloc[0]
        
        return name
    
    def getKitchenID(self):
        
        kid = self.df[self.df['name'].str.contains(self.kitchenKey)]['name'].index[0]
        
        return kid

    def getBathroomName(self):
        
        name = self.df[self.df['name'].str.contains(self.bathroomKey)]['name'].iloc[0]
        
        return name
    

    def getBathroomID(self):
        
        bid = self.df[self.df['name'].str.contains(self.bathroomKey)]['name'].index[0]
       
        return bid

    def getLaundryID(self):
        
        if (len(self.df[self.df['name'].str.contains(self.laundryKey)]['name']) > 0):
            lid = self.df[self.df['name'].str.contains(self.laundryKey)].index[0]
        else:
            lid = self.getBathroomID()
            
        return lid

    def getLaundryName(self):
        
        lid = self.getLaundryID()
        return self.df.loc[lid,'name']

    def getToiletName(self):
        
        if (len(self.df[self.df['name'].str.contains(self.toiletKey)]['name']) > 0):
            tid = self.df[self.df['name'].str.contains(self.toiletKey)].index[0]
        else:
            tid = self.getBathroomID()

        tname = self.df.loc[tid,'name']
        return tname
            

    def getAllBedroomsNames(self,sortingMethod='None'):
        
        bedroomsdf = self.df[self.df['name'].str.contains(self.bedroomsKey)]
        
        if sortingMethod == 'Volume':
            bedrooms = bedroomsdf.sort_values(by='Vol',ascending=False)['name'].values

        else:
            bedrooms = bedroomsdf['name'].values
            
        return list(bedrooms)
        
    def getNumberOfBedrooms(self):
        
        return len(self.df[self.df['name'].str.contains(self.bedroomsKey)])
        

    def isKitchenOpen(self):
        
        if self.getKitchenName()[0] == 'O':
            return True
        else:
            return False

class initialZonesConcentrations():
    
    def __init__(self):
               
        self.df = pd.DataFrame()
        self.headers = []
        
        
    def read(self,fileReader,currentLine):

        nConcentrations, self.comment = currentLine.split('!')
        self.nConcentrations = int(nConcentrations)

        if (self.nConcentrations != 0):
        
            self.headers = fileReader.readline().split()
            self.headers.remove('!')
        
            ncols = len(self.headers)-1
            nlines = int(self.nConcentrations/ncols)
            
            self.df = pd.DataFrame(columns=self.headers[1:])
            self.df.index.name = self.headers[0]

            
            for i in range(nlines):
                
                values = fileReader.readline().split()
                index = values[0]
                self.df.loc[index,:] = values[1:]
        
    def write(self,g):

        g.write(str(self.nConcentrations)+' ! '+self.comment)
        
        g.write('! '+self.df.index.name+' ')
        [ g.write(c+' ') for c in self.df.columns]
        g.write('\n')

        self.df.to_csv(g,header=False,sep=' ',line_terminator='\n')
               
        
        #to write
        return
        
    def addInitConcentration(self,pollutantName,userUnitValue,unit,MM=0):
        
        
        kgkgValue = contaminants().convertConcentrations(userUnitValue,unit,MM)
        
        self.df.loc[:,pollutantName] = kgkgValue
        self.nConcentrations = len(self.df.columns)*len(self.df.index)
    
    
        
class ahs:

    def __init__(self):
        self.headers=['#','zr#','zs#','pr#','ps#','px#','color','name']
        self.df=pd.DataFrame(columns=self.headers)
        
    def read(self,filereader,currentline):
    
        nahs,self.comment=currentline.split('!')
        self.nahs=int(nahs)
        self.contamheader=filereader.readline()
        
        for n in range(self.nahs):
            fields=filereader.readline().split()
            mydict={self.headers[i]:fields[i] for i in range(len(fields))}
            mydict['description']=filereader.readline()
        
        self.df = pd.concat([self.df,pd.DataFrame.from_records([mydict])])
        self.df.index=self.df['#'].astype(int)
        self.df.drop(['#'],axis=1,inplace=True)
    
        self.df=convert_cols(self.df)

class flowelements:

    #id icon dtype name
    #comment 
    #value1 value2 value3 ...

    #chosen structure: dataframes
    
    # id icon dtype name comment [values,...]

    def __init__(self):
        self.headers=['id','icon','dtype','name','comment','values']
        self.df=pd.DataFrame()

    def readCONTAMflowelements(self,filereader,currentline):
    
        nelems,self.comment=currentline.split('!')
        self.nelems=int(nelems)
        
        for n in range(self.nelems):
            fields=filereader.readline().split()
            mydict={self.headers[i]:fields[i] for i in range(len(fields))}

            comment=filereader.readline()
        
            mydict['comment']=comment
            mydict['values']=filereader.readline().split()  #SPEC ok for one liners only !!!
            
            self.df = pd.concat([self.df,pd.DataFrame.from_records([mydict])])

        self.df.index=self.df['id'].astype(int)
        self.df.drop(['id'],axis=1,inplace=True)

        self.df=convert_cols(self.df)
    

    def createNewElementFromExistingOne(self,existingElementName,newElementName,newComment):

    
        self.nelems += 1
        
        newElem = self.df[self.df['name']==existingElementName]
        
        newElem.index = [self.nelems]
        newElem.loc[self.nelems,'name'] = newElementName
        newElem.loc[self.nelems,'comment'] = newComment
        

        self.df = pd.concat([self.df,newElem])
        
    
    def addflowelem(self,elemtype,valuesdict):
    
        # elemtype: NSV, NT
        comment={'NSV':'Natural supply vent',
                 'NT':'Natural transfer opening',
                 'SR_NSV':'Self regulating Natural Supply Vent',
                 'OD':'Open Door',
                 'IL':'InternalLeak',
                 'VCC': 'Ventilative cooling component',
                 'RW': 'Roof window',
                 'NW': 'Normal window',
                 'D': 'Two ways door'}
        
    
        if (elemtype in ['NSV','NT','SR_NSV']):
            #2 23 plr_qcn Gen_NSV
            #Generic model for Natural Supply Vent (1m3/h at 1Pa)
            #1.63401e-007 0.000277778 0.5
            qv=1/3600 #1 m3/h²
            dp=valuesdict['dp']
            n=0.5
            
            Cturb=qv/(dp**n)
            Clam=self.Clam(Cturb,n)
            
            self.nelems+=1

            self.df.loc[self.nelems,'icon']=int(23)
            self.df['icon']=self.df['icon'].astype(int)

            if elemtype in ['NSV','NT']:

                self.df.loc[self.nelems,'dtype']='plr_qcn'
                #self.df.loc[self.nelems,'values']=[Clam,Cturb,n]
                self.df.at[self.nelems,'values']=[Clam,Cturb,n]


            elif (elemtype in ['SR_NSV']):
            
                Qmax=1.5 #1.5 times nominal for P3 NSV
                Qnom = 1.0
                
                dPmax=(Qmax/Qnom)**2 * dp  # Pressure corresponding to 1.5 nominal flow, pressure from which the curve is broken
                                           # Can be directly derived from nominal dp and flow equation 

                
                # Given the formula :  Q = Q0*( 1 - exp(dp/dP0) )
                # Q0 is the max reachable (1.5 in this case)
                # Exp(-dp/dp0) is a negative expontential --> when  dp/dp0 = 3 (aka 3 times constant), its value is 0.05 (aka, 95percent of the final value)
                # We target that this point correspond to Pmax  
                #  Pmax/dp0 = 3 <-->  dp0 = Pmax/3
                self.df.loc[self.nelems,'dtype']='srv_jwa'
                self.df.loc[self.nelems,'values']=[Qmax/3600,dPmax/3,1,4,0]

                # 5 23 srv_jwa SR_SSV
                # comment
                # values 0.000416667 0.75 1 4 0
                # Order:
                #  Q in m3/s
                #  dp0
                #  f (factor for revese flow)
                #  flow units of the GUI (4 for m3/h)
                #  pressure units of the GUI (0 for Pa)

            
            self.df.loc[self.nelems,'name']=elemtype+'_'+str(dp)+'Pa'
            self.df.loc[self.nelems,'comment']=comment[elemtype]+' 1m3/h at '+str(dp)+'Pa - by Python'

            self.df=convert_cols(self.df)
            
            
        if elemtype == 'IL':
            #internal leak
            #per default : 10 m3/h at 2Pa
            
            dp=valuesdict['dp']
            flow=valuesdict['flowRate']
            n=valuesdict['exponent']
            
            qv=flow/3600 #1 m3/h²
            
            Cturb=qv/(dp**n)
            Clam=self.Clam(Cturb,n)
            
            self.nelems+=1

            self.df.loc[self.nelems,'icon']=int(23)
            self.df['icon']=self.df['icon'].astype(int)

            self.df.loc[self.nelems,'dtype']='plr_qcn'
            self.df.at[self.nelems,'values']=[Clam,Cturb,n]
            self.df.loc[self.nelems,'name']=elemtype
            self.df.loc[self.nelems,'comment']='Internal leak - '+str(flow)+' m3/h at '+str(dp)+'Pa - by Python'
            self.df=convert_cols(self.df)



        if elemtype == 'OD':
            
            # Power law 
            #   Qv [m3/s]  = C*(dp)**0.5
            
            # discharge coefficient
            #   m_dot = Cd*A*sqrt(2*rho*dp)
            #  m_dot/rho =  Cd*A * sqrt(2/rho) * sqrt(dp)
            # Qv [m3/s] = Cd*A*sqrt(2/rho) * (dp)**0.5
            
            
            #   C  = Cd*A*sqr(2/rho)
            
            Cd = 0.6
            Area = 2.0
            rho = 1.2

            n=0.5            
            Cturb = Cd*Area*np.sqrt(2/rho)
            Clam=self.Clam(Cturb,n)
       
            self.nelems+=1

            self.df.loc[self.nelems,'icon']=int(25)
            self.df['icon']=self.df['icon'].astype(int)
            self.df.loc[self.nelems,'dtype']='plr_qcn'
            self.df.at[self.nelems,'values']=[Clam,Cturb,n]
            self.df.loc[self.nelems,'name']=elemtype
            self.df.loc[self.nelems,'comment']='Open door - by Python'
            self.df=convert_cols(self.df)


        if elemtype == 'VCC':
            # 5 23 plr_qcn Gen_VCC
            #Generic model for Ventilative Cooling (1m3/h at 1Pa)
            #1.63401e-07 0.000277778 0.5
            
            n=0.5
            rho=1.2
            Cturb=np.sqrt(2/rho)
            Clam=self.Clam(Cturb,n)
            self.nelems+=1

            self.df.loc[self.nelems,'icon']=int(23)
            self.df['icon']=self.df['icon'].astype(int)
            self.df.loc[self.nelems,'dtype']='plr_qcn'
            self.df.at[self.nelems,'values']=[Clam,Cturb,n]
            self.df.loc[self.nelems,'name']=elemtype+'_'+str(11)
            self.df.loc[self.nelems,'comment']='Ventilative cooling component by Python'
            self.df=convert_cols(self.df)
            
        if elemtype =='RW': 
            #8 27 dor_door Window-Cd06 
            #0.8 x 1.25 Window (1.0 m2) - Cd 0.6 (full opening))
            # 0.0234146 0.848528 0.5 0.01 1.25 0.8 0.6 0 0 0  
            #lam // laminar flow coefficient (R4)
            #turb // turbulent flow coefficient (R4)
            #expt // pressure exponent (R4)
            #dTmin // minimum temperature difference for two-way flow [C] (R4)
            #// Not used since version 2.4.
            #ht // height of doorway [m] (R4)
            #wd // width of doorway [m] (R4)
            #cd // discharge coefficient
            #u_T // units of temperature (I2) {W}
            #u_H // units of height (I2) {W}
            #u_W // units of width (I2) {W}
           
            #model dor_door C_turb = np.sqrt(2)*A*Cd without rho
            #toit pente 35 et fenetre ouverte
           
            rho=1.2
            n=0.5
            h=valuesdict['h']*0.573576
            w=valuesdict['w']*valuesdict['h']/h
            A=float(valuesdict['h']*valuesdict['w'])
            Cd=0.6
            Cturb=np.sqrt(2)*A*Cd
            Cturb_bis=np.sqrt(2/rho)*A*Cd
            
            Clam=self.Clam(Cturb_bis,n) # pas exactement ok
            self.nelems+=1
  
            self.df.loc[self.nelems,'icon']=int(27)
            self.df['icon']=self.df['icon'].astype(int)
            self.df.loc[self.nelems,'dtype']='dor_door'
            self.df.at[self.nelems,'values']=[Clam,Cturb,n,0.01,h,w,Cd,0,0,0]
            self.df.loc[self.nelems,'name']=elemtype+'_'+str(float(valuesdict['h']))+'_'+str(float(valuesdict['w']))
            
           
            self.df.loc[self.nelems,'comment']='Roofwindow- by Python'
            self.df=convert_cols(self.df)
            
        if elemtype =='NW': 
            #8 27 dor_door Window-Cd06 
            #0.8 x 1.25 Window (1.0 m2) - Cd 0.6 (full opening))
            # 0.0234146 0.848528 0.5 0.01 1.25 0.8 0.6 0 0 0  
            #lam // laminar flow coefficient (R4)
            #turb // turbulent flow coefficient (R4)
            #expt // pressure exponent (R4)
            #dTmin // minimum temperature difference for two-way flow [C] (R4)
            #// Not used since version 2.4.
            #ht // height of doorway [m] (R4)
            #wd // width of doorway [m] (R4)
            #cd // discharge coefficient
            #u_T // units of temperature (I2) {W}
            #u_H // units of height (I2) {W}
            #u_W // units of width (I2) {W}
            #model dor_door C_turb = np.sqrt(2)*A*Cd without rho
            # fenetre ouverte
              
            n=0.5
            Cd=0.6
            rho=1.2
            h=valuesdict['h']
            w=valuesdict['w']
            A=valuesdict['h']*valuesdict['w']  
            Cturb=np.sqrt(2)*A*Cd
            Cturb_bis=np.sqrt(2/rho)*A*Cd
            
            Clam=self.Clam(Cturb_bis,n)# pas exactement ok
            self.nelems+=1
            
          
            self.df.loc[self.nelems,'icon']=int(27)
            self.df['icon']=self.df['icon'].astype(int)
            self.df.loc[self.nelems,'dtype']='dor_door'
            self.df.at[self.nelems,'values']=[Clam,Cturb,n,0.01,h,w,0.6,0,0,0]
            self.df.loc[self.nelems,'name']=elemtype+'_'+str(float(h))+'_'+str(float(w))
            #'NW'+'_'+str(float(W['Height']))+'_'+str(float(W['Width']))
            self.df.loc[self.nelems,'comment']='Normalwindow - by Python'
            self.df=convert_cols(self.df)    
            
        if elemtype =='D':
       
            #8 27 dor_door Window-Cd06 
            #0.8 x 1.25 Window (1.0 m2) - Cd 0.6 (full opening))
            # 0.0234146 0.848528 0.5 0.01 1.25 0.8 0.6 0 0 0  
            #lam // laminar flow coefficient (R4)
            #turb // turbulent flow coefficient (R4)
            #expt // pressure exponent (R4)
            #dTmin // minimum temperature difference for two-way flow [C] (R4)
            #// Not used since version 2.4.
            #ht // height of doorway [m] (R4)
            #wd // width of doorway [m] (R4)
            #cd // discharge coefficient
            #u_T // units of temperature (I2) {W}
            #u_H // units of height (I2) {W}
            #u_W // units of width (I2) {W}
            #model dor_door C_turb = np.sqrt(2)*A*Cd without rho
            # fenetre ouverte
           
            n=0.5
            Cd=0.6
            rho=1.2
            h=valuesdict['h']
            w=valuesdict['w']
            A=float(valuesdict['h']*valuesdict['w'])
            Cturb=np.sqrt(2)*A*Cd
            Cturb_bis=np.sqrt(2/rho)*A*Cd
            Clam=self.Clam(Cturb_bis,n)# pas exactement ok
            self.nelems+=1
          
            self.df.loc[self.nelems,'icon']=int(27)
            self.df['icon']=self.df['icon'].astype(int)
            self.df.loc[self.nelems,'dtype']='dor_door'
            self.df.at[self.nelems,'values']=[Clam,Cturb,n,0.01,h,w,0.6,0,0,0]
            self.df.loc[self.nelems,'name']=elemtype+'_'+str(float(h))+'_'+str(float(w))
            self.df.loc[self.nelems,'comment']='Two ways door - by Python'
            self.df=convert_cols(self.df)    
            #print(elemtype+'_'+str(float(h))+'_'+str(float(w)))
          
      
      
            
    def Clam(self,Ct,n):
        rho=1.2041
        mu=1.81625e-5
        Re=30

        
        A=np.sqrt(rho/2)*Ct/0.6
        D=np.sqrt(A)
        Ftrans=mu*Re*A/D
        dPtrans=(Ftrans/(Ct*rho))**(1/n)

        
        Clam=mu*Ftrans/(rho*dPtrans)
        
        return Clam

        
    
    def writeCONTAMflowelements(self,g):
        g.write(str(self.nelems)+' !'+self.comment)
        
        for i in self.df.index:
            g.write(str(i)+' ')
            [g.write(str(self.df.loc[i,c])+' ') for c in ['icon','dtype','name']]
            g.write('\n')
            g.write(self.df.loc[i,'comment'])
            
            if ('\n' not in self.df.loc[i,'comment']):
                g.write('\n')
            
            [g.write(str(v)+' ') for v in self.df.loc[i,'values']]
            g.write('\n')


class filterElements:

    def __init__(self):
        self.headers=['id','ftype','area','depth','density','ual','ud','name']
        self.df=pd.DataFrame()
        self.description=''
        self.efficiencies={}
        self.nelems=0

    def read(self,filereader,currentline):
    
        nelems,self.comment=currentline.split('!')
        self.nelems=int(nelems)
        
        if (self.nelems==0):
            return
        
        for n in range(self.nelems):
            fields=filereader.readline().split()
            mydict={self.headers[i]:fields[i] for i in range(len(fields))}

            description=filereader.readline()       
            mydict['description']=description
            
            nLines = int(filereader.readline())
            efficiencyDict = {}
            
            for line in range(nLines):
                specie,efficiency = filereader.readline().split()
                efficiencyDict[specie] = float(efficiency)
            
            mydict['efficiencies']=efficiencyDict
            dictAsString = str(efficiencyDict)
            
            self.df = pd.concat([self.df,pd.DataFrame.from_records([dictAsString])],ignore_index=True)
            
        self.df.index=self.df['id'].astype(int)
        self.df.drop(['id'],axis=1,inplace=True)

        self.df=convert_cols(self.df)


    
    def write(self,g):
    
        g.write(str(self.nelems)+' !'+self.comment)
        
        if ('id' in self.headers):
            self.headers.remove('id')
        
        for i in self.df.index:
            g.write(str(i)+' ')
            [g.write(str(self.df.loc[i,c])+' ') for c in self.headers]
            g.write('\n')
            g.write(self.df.loc[i,'description'])
            if ('\n' not in self.df.loc[i,'description']):
                g.write('\n')


            dictAsString = self.df.loc[i,'efficiencies']
            efficienciesDict = eval(dictAsString)
            
            g.write(str(len(efficienciesDict))+'\n')
 
            for key,value in efficienciesDict.items() :
                g.write(key+' '+str(value)+'\n')


    def add(self,paramsDict):
    
        #expected paramsDict {'name':'shortName','description':'long description',efficiencies{'specie1':'Efficiency1','specie2':efficiency2}
        
        self.nelems+=1
        
        self.df.loc[self.nelems,'name']=paramsDict['Name']
        self.df.loc[self.nelems,'description']=paramsDict['Description']

        
        self.df.loc[self.nelems,'efficiencies']= str(paramsDict['Efficiencies'])
        # storing dictionaries in dataframe cells is not consisten across pandas versions
        # for some version putting the dict in brackets works, but for some is stores an array
        # store as string, and then evaluate the dictionnary with eval
        
        #Default values for constant efficiency filters
        fields=['ftype','area','depth','density','ual','ud']
        values=['cef', 1, 0.1, 100, 0, 0]
        
        for field,value in zip(fields,values):
            self.df.loc[self.nelems,field]=value


        self.df=convert_cols(self.df)


class filters:

    def __init__(self):
    
        #self.nelems = 0
        self.df = pd.DataFrame()

        self.headers=['nr','fe','sub']

    def read(self,filereader,currentline):

        nelems,self.comment=currentline.split('!')
        self.nelems=int(nelems)
        
        if (self.nelems==0):
            return
        
        for n in range(self.nelems):
            fields=filereader.readline().split()
            myDict = { header:field for header,field in zip(self.headers,fields) }
            values=filereader.readline().split()
            myDict['values']=values
            self.df = pd.concat([self.df,pd.DataFrame.from_records([myDict])])
            
            
        self.df.index=self.df['nr'].astype(int)
        self.df.drop(['nr'],axis=1,inplace=True)

        self.df=convert_cols(self.df)
 
            
    def write(self,g):

        if ('nr' in self.headers):
            self.headers.remove('nr')

    
        g.write(str(self.nelems)+' !'+self.comment)
        
        for i in self.df.index:
            g.write(str(i)+' ')
            [g.write(str(self.df.loc[i,c])+' ') for c in self.headers]
            g.write('\n')
            
            [ g.write(v+' ') for v in self.df.loc[i,'values']]
            g.write('\n')
          

    def add(self,filterElementName,filterElementsObject):

        
        filterElementIndex = filterElementsObject.df[ filterElementsObject.df['name'] == filterElementName ].index[0]
        
        self.nelems += 1
        serie = pd.Series({'fe':filterElementIndex , 'sub' : 1 , 'values':['0','0']})
        serie.name = self.nelems
        
        
        #self.df = self.df.append(serie)
        self.df = pd.concat([self.df,pd.DataFrame(serie).T])
        
        #self.df.loc[self.nelems,'fe'] = filterElementIndex
        #self.df.loc[self.nelems,'sub'] = 1
        #self.df.loc[self.nelems,'values'] = (['0','0'])
        self.df=convert_cols(self.df)
        
        
        return self.nelems
        
          
class contaminants:

    def __init__(self):
    
        self.myheaders=['#','s','t','molwt','mdiam','edens','decay','Dm','CCdef','Cp','Kuv','u0','u1','u2','u3','u4','name']
        # # s t   molwt    mdiam       edens       decay         Dm         CCdef        Cp          Kuv     u[5]      name
        
        self.df=pd.DataFrame(columns=self.myheaders)
        
        
        self.unitcodes = {'ppm':1, 'ug/m3':13}

        
    def read(self,filereader,currentline):
        
        nctm,self.comment1=currentline.split('!')
        self.ctmlist=filereader.readline().split()
        nspecies,self.comment2=filereader.readline().split('!')
        
        self.nctm=int(nctm)
        self.nspecies=int(nspecies)
        
        self.contamheaders=filereader.readline()
        
        for s in range(self.nspecies):
               
            fields=filereader.readline().split()

            mydict={self.myheaders[i]:fields[i] for i in range(len(self.myheaders))}
            mydict['description']=filereader.readline()
            self.df = pd.concat([self.df,pd.DataFrame.from_records([mydict])])
            
        self.df.index=self.df['#'].astype(int)
        self.df.drop(['#'],axis=1,inplace=True)

        self.df=convert_cols(self.df)
        #print(self.df)

    def write(self,g):
    
        
        g.write(str(self.nctm)+' ! '+self.comment1)
        [g.write(c+' ') for c in self.ctmlist]
        g.write('\n')
        g.write(str(self.nspecies)+' ! '+self.comment2)
        g.write(self.contamheaders)
        
        towrite=list(self.df.columns)
        towrite.remove('description')
        
        for i in self.df.index:
        
            g.write(str(i)+' ')
            [g.write(str(self.df.loc[i,c])+' ') for c in towrite]
            g.write('\n')
            g.write(self.df.loc[i,'description']) 
            
            if ('\n' not in self.df.loc[i,'description']):
                g.write('\n')

    def addSpecie(self,specieName,defaultConcentration,unit='kg/kg',molarMass=0):
      
        self.nspecies += 1
        specieID = self.nspecies
        
        
        if unit != 'kg/kg':
            defaultConcentration = self.convertConcentrations(defaultConcentration,unit, molarMass)
            unitcode = self.getUnitCode(unit)
        else:
            unitcode=0
        
        nonNullDefaultsValues={'s':1,'Dm':2e-5,'Cp':1000,'molwt':molarMass,'ccdef':defaultConcentration,'u0':unitcode}



        self.df.loc[specieID,'name'] = specieName
        self.df.loc[specieID,'CCdef'] = defaultConcentration
        self.df.loc[specieID,'description'] = specieName+' - added by Python'
        
        
        for key,value in nonNullDefaultsValues.items():
            self.df.loc[specieID,key] = value
            
        self.df.fillna(0,inplace=True)
        
        self.df=convert_cols(self.df)

        self.nctm += 1              
        self.ctmlist.append(str(specieID))        

        return


    def getUnitCode(self,unitName):
        
        return self.unitcodes[unitName]

    def getUnitNameFromCode(self,unitCode):
        
        reversedDict = {v:k for k,v in self.unitcodes.items()}
        
        unitName = reversedDict[unitCode]
        
        return unitName
        

    def getUnitName(self,contaminantName):
        
        
        specieID = self.df[self.df['name']==contaminantName].index[0]
        specieUnitCode = self.df.loc[specieID,'u0']
        
        unitName = self.getUnitNameFromCode(specieUnitCode)
        
        return unitName
        

    def convertConcentrations(self,value,fromUnit,MM=0):
        #convert any unit to kg/kg
        
        Vs= 24.05 #volume of 1 kmol in standard conditions
        rho_air = 1.204 # at 20 de

        if fromUnit == 'ppm':
            #kg/kg = (ppm x MM) / (1 000 000 xVs x rho_air)
            
            return value*MM/(1e6*Vs*rho_air)

        elif fromUnit == 'ug/m3':
           
            return value*1e-9/rho_air

        else:
            raise ValueError("Unknown unit "+fromUnit+".Currently accepted units are ug/m3 and ppm")


    def kgkgToUnit(self,unitName):
        
        return 1/self.convertConcentrations(1,unitName)

    



class sourceElements:
    #15 ! source/sink elements:
    #1 H2O bls Buffer_H2O
    #Vochtbuffering
    #0.0003 1.2 6.23 1.18 0 0 0

    def __init__(self):
        self.sources={}
        self.nsources=0
        
    def read(self,filereader,currentline):
            
        nsources,comment=currentline.split('!')
        self.nsources=int(nsources)
        self.comment=comment
        
        for i in range(self.nsources):
        
            sid,specie,stype,name=filereader.readline().split()
            description=filereader.readline()
            values=filereader.readline().split()
            
            sdict={}
            sdict['specie']=specie
            sdict['source type']=stype
            sdict['name']=name
            sdict['description']=description
            sdict['values']=values
            
            self.sources[int(sid)]=sdict
            
        
            
            
    def write(self,g):
    
        g.write(str(self.nsources)+' ! '+self.comment)
        if ('\n' not in self.comment):
            g.write('\n')

        for k,v in self.sources.items():
        
            g.write(str(k)+' '+v['specie']+' '+v['source type']+' '+v['name'])

            if ('\n' not in v['name']):
                g.write('\n')

            g.write(v['description'])
            if ('\n' not in v['description']):
                g.write('\n')
            
            [ g.write(str(x)+' ') for x in v['values'] ]
            g.write('\n')
    
    def getSourceID(self,source_name):
        
        for sid,svalues in self.sources.items():
            
            if (svalues['name']==source_name):
                return sid
                
                
        return 0
                
    
    def addConstantRateSourceElement(self,specie,stype,name,description,rate,unitName):
        
        #rate should be kg/s
        #unit if fake for now
        unitIndex = {'kg/s':0,'L/s':9, 'L/h':33, 'ug/h':30}
        
        
        self.nsources += 1
        
        sdict={}
        sdict['specie']=specie
        sdict['source type']=stype
        sdict['name']=name
        sdict['description']=description
        sdict['values'] = [ self.toKilosPerSeconds(unitName,rate),0,unitIndex[unitName],0]
            
        self.sources[self.nsources]=sdict

            
        
    def toKilosPerSeconds(self,unitName,value):
        
        if unitName == 'ug/h':
            
            return value/1e9/3600
        
    
    
                         
class sources:

    #! #  z#  e#  s#  c#  mult   CC0  (X, Y, H)min  (X, Y, H)max u[1] cdvf <cdvf name> cfd <cfd name>
    #1   5  10   0   0    10     0  0 0 0  0 0 0  0 0 0
    #2   5   9   0   0     1     0  0 0 0  0 0 0  0 0 0
     
    def __init__(self):
        self.headers=['#','z','e','s','c','mult','CC0','xmin','ymin','hmin','xmax','ymax','hmax','color','u','cdvf','cfd']
        self.df=pd.DataFrame(columns=self.headers)
        self.comment='source/sinks:\n'
        
    def read(self,filereader,currentline):
        nsources,self.comment=currentline.split('!')
        
        self.nsources=int(nsources)

        fileheaders=filereader.readline() #do not use that one since not well structured - read but unused
               
        for i in range(self.nsources):
        
            fields=filereader.readline().split()
            mydict={self.headers[i]:fields[i] for i in range(len(fields))}

            self.df = pd.concat([self.df,pd.DataFrame.from_records([mydict])])
        
        self.df.index=self.df['#'].astype(int)
        self.df.drop(['#'],axis=1,inplace=True)
            
        #print(self.df)    
        #self.headers.remove('#')
        self.df=convert_cols(self.df)


    def write(self,g):
    
        g.write(str(len(self.df))+' ! '+self.comment)
        g.write('! ')
        [ g.write(x+' ') for x in self.headers ]
        g.write('\n')
        
        self.df.to_csv(g,header=False,sep=' ',line_terminator='\n')
        
        
    def addSource(self,roomid,sourceElemid,scheduleid,ctrlid,mult,CC0=0):

        dict_to_append={'z':roomid,'e':sourceElemid,'s':scheduleid,'c':ctrlid,'mult':mult,'CC0':CC0}
        for c in self.df.columns:
            if c not in dict_to_append.keys():
                dict_to_append[c]=int(0)    

        #self.df=self.df.append({'z':roomid,'e':sourceElemid,'s':scheduleid,'c':ctrlid,'mult':mult,'CC0':CC0},ignore_index=True)
        self.df = pd.concat([self.df,pd.DataFrame.from_records([{'z':roomid,'e':sourceElemid,'s':scheduleid,'c':ctrlid,'mult':mult,'CC0':CC0}])],ignore_index=True)


        for c in ['z','e','s','c']:
            self.df[c]=self.df[c].astype(int)
        
        self.df.fillna(0,inplace=True)
        self.df=convert_cols(self.df)
        if (self.df.index[0]==0):
            self.df.index=[ x+1 for x in self.df.index]
        
   
    
   
    
class controlnodes:

    def __init__(self):
    
        self.df=pd.DataFrame()

    def read(self,filereader,currentline):
    
        nctrl,self.comment=currentline.split('!')
        
        self.nctrl=int(nctrl)
        
        if (self.nctrl==0):
            
            self.headers=['#','typ','seq','f','n','c1','c2','name']
            
        else:      
            self.headers=filereader.readline().replace('!','').split()
        
        #headers.append('description')
        #headers.append('values')
        
        self.df=pd.DataFrame(columns=self.headers+['description','values'])
        
        #if (self.nctrl==0):
        #   print(self.df)
        #   self.df.columns=list(self.df.columns)+['description','values']
        #   print(self.df.columns)
        
        for ctrlid in range(self.nctrl):
            
            mydict={k:v for k,v in zip(self.headers,filereader.readline().split())}
            
            mydict['description']=filereader.readline()
            mydict['values']=filereader.readline().split()
                    
            self.df = pd.concat([self.df,pd.DataFrame.from_records([mydict])])


            
        self.df.index=self.df['#'].astype(int)
        self.df.drop(['#'],axis=1,inplace=True)
        
        #print(self.df)    
        self.headers.remove('#')
        self.df=convert_cols(self.df)
        
        

    def write(self,g):
    
        #print(self.headers)
    
        g.write(str(self.nctrl)+' !'+self.comment)
        
        g.write('! # ')
        [g.write(h+' ') for h in self.headers]
        g.write('\n')
        
        for i in self.df.index:
            g.write(str(i)+' ')

            [g.write(str(self.df.loc[i,c])+' ') for c in self.headers]
            g.write('\n')
            g.write(self.df.loc[i,'description'])
            
            if ('\n' not in self.df.loc[i,'description']):
                g.write('\n')
            
            [g.write(str(v)+' ') for v in self.df.loc[i,'values']]
            g.write('\n')
    
       
    def addspeciesensor(self,zonesdf,roomid,specie_name,name,description='',multiplier=1,unit=''):
        
        name = shortenTooLongName(name,15)
        
        if (roomid != -1):       
            roomname=zonesdf.loc[roomid,'name']
        else:
            roomname = 'EXT'

    
        self.nctrl+=1
        
        self.df.loc[self.nctrl,'typ']='sns'
        
        self.df.loc[self.nctrl,'seq']=int(self.nctrl)
        self.df.loc[self.nctrl,'f']=int(0)
        self.df.loc[self.nctrl,'n']=int(0)
        self.df.loc[self.nctrl,'c1']=int(0)
        self.df.loc[self.nctrl,'c2']=int(0)
        self.df.loc[self.nctrl,'name']=name
        
        values=[0, 1, 0, 0, roomid, 1, 0, 0.0,0.0, 0.0, 0, specie_name]

        self.df.loc[self.nctrl,'description']='zone sensor by Python'
       
        self.df.at[self.nctrl,'values']=[ str(v) for v in values]
    
        #typ seq f n  c1  c2 name
    
        #sns data
        # offset // offset value (R4)
        # scale // scale value (R4)
        # tau // time constant (R4)
        # oldsig // signal at last time step - for restart (R4)
        # source // index of source (source not defined at read time) (IX)
        # type // type of source: 1=zone, 2=path, 3=junction, 4=duct,
        # // 5=exp, 6=term (I2)
        # measure // 0=contaminant, 1=temperature, 2=flow rate, 3=dP,
        # // 4=Pgage, 5=zone occupancy (I2)
        # X // X-coordinate of sensor [m] (R4)
        # Y // Y-coordinate of sensor [m] (R4)
        # relHt // relative height of sensor [m] (R4)
        # units[] // units of coordinates {W} (I1)
        # species[] // species name [I1]; convert to pointer


        self.addreport(self.nctrl,specie_name+'_'+roomname,specie_name,multiplier=multiplier,unit=unit)

    def addoccupancysensor(self,zonesdf,roomid,name,description=''):
        
        roomname=zonesdf.loc[roomid,'name']
    
        self.nctrl+=1
        
        self.df.loc[self.nctrl,'typ']='sns'
        
        self.df.loc[self.nctrl,'seq']=int(self.nctrl)
        self.df.loc[self.nctrl,'f']=int(0)
        self.df.loc[self.nctrl,'n']=int(0)
        self.df.loc[self.nctrl,'c1']=int(0)
        self.df.loc[self.nctrl,'c2']=int(0)
        self.df.loc[self.nctrl,'name']=name
        
        values=[0, 1, 0, 0, roomid, 1, 5, 0.0,0.0, 0.0, 0, 'Occupancy']

        self.df.loc[self.nctrl,'description']='zone occupancy sensor by Python'
       
        self.df.at[self.nctrl,'values']=[ str(v) for v in values]
    
        #typ seq f n  c1  c2 name
    
        #sns data
        # offset // offset value (R4)
        # scale // scale value (R4)
        # tau // time constant (R4)
        # oldsig // signal at last time step - for restart (R4)
        # source // index of source (source not defined at read time) (IX)
        # type // type of source: 1=zone, 2=path, 3=junction, 4=duct,
        # // 5=exp, 6=term (I2)
        # measure // 0=contaminant, 1=temperature, 2=flow rate, 3=dP,
        # // 4=Pgage, 5=zone occupancy (I2)
        # X // X-coordinate of sensor [m] (R4)
        # Y // Y-coordinate of sensor [m] (R4)
        # relHt // relative height of sensor [m] (R4)
        # units[] // units of coordinates {W} (I1)
        # species[] // species name [I1]; convert to pointer

        self.addreport(self.nctrl,'O_'+roomname)


    def addexposuresensor(self,oid,specie_name,description='',multiplier=1):
        
        self.nctrl+=1
        
        self.df.loc[self.nctrl,'typ']='sns'
        
        name=str(oid)+'_'+specie_name+'_sensor'
        mult=1
        
        self.df.loc[self.nctrl,'seq']=int(self.nctrl)
        self.df.loc[self.nctrl,'f']=int(0)
        self.df.loc[self.nctrl,'n']=int(0)
        self.df.loc[self.nctrl,'c1']=int(0)
        self.df.loc[self.nctrl,'c2']=int(0)
        self.df.loc[self.nctrl,'name']=name
        
        values=[0, mult, 0, 0, oid, 5, 0, 0.0,0.0, 0.0, 0, specie_name]

        self.df.loc[self.nctrl,'description']='occupant sensor by Python'
       
        self.df.at[self.nctrl,'values']=[ str(v) for v in values]
    
        #typ seq f n  c1  c2 name
    
        #sns data
        # offset // offset value (R4)
        # scale // scale value (R4)
        # tau // time constant (R4)
        # oldsig // signal at last time step - for restart (R4)
        # source // index of source (source not defined at read time) (IX)
        # type // type of source: 1=zone, 2=path, 3=junction, 4=duct,
        # // 5=exp, 6=term (I2)
        # measure // 0=contaminant, 1=temperature, 2=flow rate, 3=dP,
        # // 4=Pgage, 5=zone occupancy (I2)
        # X // X-coordinate of sensor [m] (R4)
        # Y // Y-coordinate of sensor [m] (R4)
        # relHt // relative height of sensor [m] (R4)
        # units[] // units of coordinates {W} (I1)
        # species[] // species name [I1]; convert to pointer
      
        self.addreport(self.nctrl,specie_name+'_O'+str(oid),specie_name,multiplier=multiplier) 




    def addflowsensor(self,pathid,report_name,description=''):

           
        self.nctrl+=1

        self.df.loc[self.nctrl,'typ']='sns'
        
        self.df.loc[self.nctrl,'seq']=int(self.nctrl)
        self.df.loc[self.nctrl,'f']=int(0)
        self.df.loc[self.nctrl,'n']=int(0)
        self.df.loc[self.nctrl,'c1']=int(0)
        self.df.loc[self.nctrl,'c2']=int(0)
        self.df.loc[self.nctrl,'name']='sensor_flow_'+str(pathid)
        
        values=[0, 1, 0, 0, pathid, 2, 2, 0.0,0.0, 0.0, 0, '<none>']

        self.df.loc[self.nctrl,'description']='flow sensor by Python'
       
        self.df.at[self.nctrl,'values']=[ str(v) for v in values]
    
        #typ seq f n  c1  c2 name
    
        #sns data
        # offset // offset value (R4)
        # scale // scale value (R4)
        # tau // time constant (R4)
        # oldsig // signal at last time step - for restart (R4)
        # source // index of source (source not defined at read time) (IX)
        # type // type of source: 1=zone, 2=path, 3=junction, 4=duct,
        # // 5=exp, 6=term (I2)
        # measure // 0=contaminant, 1=temperature, 2=flow rate, 3=dP,
        # // 4=Pgage, 5=zone occupancy (I2)
        # X // X-coordinate of sensor [m] (R4)
        # Y // Y-coordinate of sensor [m] (R4)
        # relHt // relative height of sensor [m] (R4)
        # units[] // units of coordinates {W} (I1)
        # species[] // species name [I1]; convert to pointer

        self.addreport(self.nctrl,report_name,'FLOW')


    def addtemperaturesensor(self,zonesdf,roomid,name):
        
        
        if (roomid != -1):       
            roomname=zonesdf.loc[roomid,'name']
        else:
            roomname = 'EXT'
    
    
        self.nctrl+=1
        
        self.df.loc[self.nctrl,'typ']='sns'
        
        self.df.loc[self.nctrl,'seq']=int(self.nctrl)
        self.df.loc[self.nctrl,'f']=int(0)
        self.df.loc[self.nctrl,'n']=int(0)
        self.df.loc[self.nctrl,'c1']=int(0)
        self.df.loc[self.nctrl,'c2']=int(0)
        self.df.loc[self.nctrl,'name']=name
        
        values=[0, 1, 0, 0, roomid, 1, 1, 0.0,0.0, 0.0, 0, name]
        
        self.df.loc[self.nctrl,'description']='Temperature sensor by Python'
       
        self.df.at[self.nctrl,'values']=[ str(v) for v in values]
    
        self.addreport(self.nctrl,'T'+'_'+roomname, 'T'+'_' + roomname)
    
    def addtemperaturesensor(self,zonesdf,roomid,name):
        
        #if (len(name)>15):
           # name=name.replace('kamer','')

        
        if (roomid != -1):       
            roomname=zonesdf.loc[roomid,'name']
        else:
            roomname = 'EXT'

    
        self.nctrl+=1
        
        self.df.loc[self.nctrl,'typ']='sns'
        
        self.df.loc[self.nctrl,'seq']=int(self.nctrl)
        self.df.loc[self.nctrl,'f']=int(0)
        self.df.loc[self.nctrl,'n']=int(0)
        self.df.loc[self.nctrl,'c1']=int(0)
        self.df.loc[self.nctrl,'c2']=int(0)
        self.df.loc[self.nctrl,'name']=name
        
        values=[0, 1, 0, 0, roomid, 1, 1, 0.0,0.0, 0.0, 0, name]
        
        self.df.loc[self.nctrl,'description']='Temperature sensor by Python'
       
        self.df.at[self.nctrl,'values']=[ str(v) for v in values]
    
        self.addreport(self.nctrl,'T'+'_'+roomname, 'T'+'_' + roomname)
    


    def addreport(self,id_to_report,name,reporttype='',description='',header='',multiplier=1,unit=''):
    
        name = shortenTooLongName(name,15)

    
        self.nctrl+=1
        
        self.df.loc[self.nctrl,'typ']='log'
        self.df.loc[self.nctrl,'seq']=int(self.nctrl)
        self.df.loc[self.nctrl,'f']=int(1)
        self.df.loc[self.nctrl,'n']=int(1)
        self.df.loc[self.nctrl,'c1']=int(id_to_report)
        self.df.loc[self.nctrl,'c2']=int(0)
        self.df.loc[self.nctrl,'name']=name
        
        #self.df.loc[self.nctrl,'description']=description
        self.df.loc[self.nctrl,'description']='Report by Python'


        # offset // offset value (R4)
        # scale // scale value (R4)
        # udef // true if using default units (I2) {W}
        # header[] // header string (I1)
        # units[] // units string (I1)
    
        scale=multiplier
        unit='n/a'
    
        if reporttype=='CO2':
            scale=(1e6*24.05*1.204)/44
            unit='ppm'
    
    
        if (reporttype=='H2O'):
            scale= 68.37 # H2O in kg/kg to RH in standardized conditions
            unit='RH'
        
        if (reporttype=='FLOW'):
            scale=2989.78
            unit='m3/h'

        

        
        values=[0,scale,0,name,unit]
        if header != '':
            values[3] = header


        #self.df.loc[self.nctrl,'values']=[ str(v) for v in values ]
        self.df.at[self.nctrl,'values']=[ str(v) for v in values ]


    def addconstant(self,name,value):
        
        name = shortenTooLongName(name,15)

        
        #! # typ seq f n  c1  c2 name
        #1 set   1 0 0   0   0 test
        #Constant value
         #1
        self.nctrl+=1
        
        self.df.loc[self.nctrl,'typ']='set'
        self.df.loc[self.nctrl,'seq']=int(self.nctrl)
        self.df.loc[self.nctrl,'f']=int(0)
        self.df.loc[self.nctrl,'n']=int(0)
        self.df.loc[self.nctrl,'c1']=int(0)
        self.df.loc[self.nctrl,'c2']=int(0)
        self.df.loc[self.nctrl,'name']=name
        
        self.df.loc[self.nctrl,'description']='Constant by Python'
        
        values=[value]
        self.df.at[self.nctrl,'values']=[ str(v) for v in values ]
    
        return self.nctrl
    
    
    def addBasicOperation(self,otype,name,input1,input2,description=''):
    
        #otype can be: sub,mul,add,div
        olist=['sub','mul','add','div']
        
        if (otype not in olist):
            print("Operation ",otype,"not programmed yet")
            exit()
    
        self.nctrl+=1
        self.df.loc[self.nctrl,'typ']=otype
        self.df.loc[self.nctrl,'seq']=int(self.nctrl)
        self.df.loc[self.nctrl,'f']=int(0)
        self.df.loc[self.nctrl,'n']=int(2)
        self.df.loc[self.nctrl,'c1']=int(input1)
        self.df.loc[self.nctrl,'c2']=int(input2)
        self.df.loc[self.nctrl,'name']=name
        
        
        if (description==''):
            description=otype+' by Python'
        else:
            description+=' - by Python'
        self.df.loc[self.nctrl,'description']=description
    
        self.df.at[self.nctrl,'values']=[ ]
    
        return self.nctrl
    
    
    def addBool(self,otype,name,input1,input2,description=''):
        
        #otype can be: sub,mul,add,div
        olist=['and']
        
        if (otype not in olist):
            print("Operation ",otype,"not programmed yet")
            exit()
    
        self.nctrl+=1
        self.df.loc[self.nctrl,'typ']=otype
        self.df.loc[self.nctrl,'seq']=int(self.nctrl)
        self.df.loc[self.nctrl,'f']=int(0)
        self.df.loc[self.nctrl,'n']=int(2)
        self.df.loc[self.nctrl,'c1']=int(input1)
        self.df.loc[self.nctrl,'c2']=int(input2)
        self.df.loc[self.nctrl,'name']=name
        
        
        if (description==''):
            description=otype+' by Python'
        else:
            description+=' - by Python'
        self.df.loc[self.nctrl,'description']=description
    
        self.df.at[self.nctrl,'values']=[ ]
    
        return self.nctrl
    
    
    
    def addMinMax(self,otype,name,inputs,description=''):
        #inputs= list of control ids
        
        if (otype not in ['min','max']):
            print("Only min and max allowed")
            exit()
            
        self.nctrl+=1
        self.df.loc[self.nctrl,'typ']=otype
        self.df.loc[self.nctrl,'seq']=int(self.nctrl)
        self.df.loc[self.nctrl,'f']=int(0)
        self.df.loc[self.nctrl,'n']=len(inputs)+1
        self.df.loc[self.nctrl,'c1']=int(0)
        self.df.loc[self.nctrl,'c2']=int(0)
        self.df.loc[self.nctrl,'name']=name


        if description=='':
            description=otype+' by Python'
        else:
            description+=' - by Python'
        self.df.loc[self.nctrl,'description']=description

        
        values=[len(inputs)]+inputs
        self.df.at[self.nctrl,'values']=[ str(v) for v in values ]
    
        return self.nctrl
    
        
    def addLinearControl(self,sensorid,qmin,qmax,cmin,cmax):
    
        # for now adding new constants, but check later if it
        # doesn't exist already
        #self.df.loc[self.nctrl,'typ']='set'
        #self.df.loc[self.nctrl,'typ']='set'

        ctrlids={}

        self.addconstant('Qmin',qmin)
        ctrlids['Qmin']=self.nctrl
        
        self.addconstant('Qmax',qmax)
        ctrlids['Qmax']=self.nctrl
        
        self.addconstant('Cmin',cmin)
        ctrlids['Cmin']=self.nctrl

        self.addconstant('Cmax',cmax)
        ctrlids['Cmax']=self.nctrl
    
        self.addBasicOperation('sub','<none>',ctrlids['Qmax'],ctrlids['Qmin'])
        ctrlids['dQmax']=self.nctrl
        self.addBasicOperation('sub','<none>',ctrlids['Cmax'],ctrlids['Cmin'])
        ctrlids['dCmax']=self.nctrl
        
        self.addBasicOperation('sub','<none>',sensorid,ctrlids['Cmin'])
        ctrlids['dCactual']=self.nctrl
        
        self.addBasicOperation('div','<none>',ctrlids['dCactual'],ctrlids['dCmax'])
        ctrlids['Ratio']=self.nctrl
        
        self.addBasicOperation('mul','<none>',ctrlids['Ratio'],ctrlids['dQmax'])
        ctrlids['product']=self.nctrl

        self.addBasicOperation('add','<none>',ctrlids['product'],ctrlids['Qmin'])
        ctrlids['unbounded']=self.nctrl
        
        self.addMinMax('min','<none>',[ctrlids['unbounded'],ctrlids['Qmax']])
        ctrlids['upperbounded']=self.nctrl
        
        self.addMinMax('max','Final',[ctrlids['Qmin'],ctrlids['upperbounded']])
        
   
    def addGreaterThanOtherSignal(self,sensorid,otherid):


        """zones=contam_data['zones']
        controls=contam_data['controls']
        
        ctrlids={}
        T_name='T_EXT'
        
        if (controls.df['name'].isin([T_name]).max() == False):
            self.addtemperaturesensor(zones.df,-1,'T-sensor')
            ctrlids['Ext']=self.nctrl
        else: 
            ctrlids['Ext']=controls.df[controls.df['name']==T_name].index[0]
        """    
        
        self.addLLS(otherid,sensorid,'Lower than')
   
    def addGreaterThanValue(self,sensorid,value):
                
        self.addconstant('constant'+str(value), value)
        constantid = self.nctrl
        
        self.addLLS(constantid,sensorid,'Lower than '+str(value))


    def addIsBetween(self,sensorid,lowervalueid,highervalueid):


        self.addLLS(lowervalueid,sensorid,'Lower than')
        lowerswitchid = self.nctrl
        self.addLLS(sensorid,highervalueid,'Lower than')
        higherswitchid = self.nctrl
        
        self.addBool('and', 'Isbetween', lowerswitchid, higherswitchid)
                
        
    

    def addCollector(self,flow_rates_ids,species_ids,description=''):
    
        #Computing a collector based on a vector of flow rates and a vector of speces
        numerators=[]
        denominators=[]
        
        
        
        for f,c in zip (flow_rates_ids,species_ids):
            
            #f: flow
            #c: concentration
            
            self.addBasicOperation('mul','<none>',f,c)
            numerators.append(self.nctrl)

            denominators.append(f)
        
        for n in numerators:
        
            if (numerators.index(n)==0):
                previous=n
                continue
       
            self.addBasicOperation('add','<none>',previous,n)
            #print("Num: Previous,current,new",previous,n,self.nctrl)
            previous=self.nctrl

        
        numid=self.nctrl
        
        for d in denominators:
        
            if (denominators.index(d)==0):
                previous=d
                continue

            self.addBasicOperation('add','<none>',previous,d)
            #print("Den: Previous,current,new",previous,d,self.nctrl)
            previous=self.nctrl
            

        denid=self.nctrl
            
        self.addconstant('<none>',1)
        self.addMinMax('max','<none>',[self.nctrl,denid],'make sur denominators not 0') #making sure the den is not 0
           
        denid=self.nctrl
        
        self.addBasicOperation('div','<none>',numid,denid,description)
        
        self.addreport(self.nctrl,'CO2_Collector')
        #def addreport(self,id_to_report,name,reporttype='',description=''):

        
    def addBalanceControl(self,balrooms,nom_flows_dict,unbal_ctrls_dict,ids):
    
        #this assumes the control have the form C_MS_roomname or C_ME_roomname
        #Then shortnames are max 10 char (as control have max 15 chars)
        shortrooms=[shortenTooLongName(x,10) for x in balrooms]
        
        supplyids=[]
        exhaustids=[]
        
        for c in unbal_ctrls_dict.keys():

            #print("Control",c)            

            room=c.split('_')[-1]

            if (room in balrooms) or (room in shortrooms):

                qnom=nom_flows_dict[c]

                self.addconstant('<none>',qnom)
                
                qid=self.nctrl
                cid=ids[unbal_ctrls_dict[c]]
                
                #print(qid,cid)
                self.addBasicOperation('mul','<none>',qid,cid,'')

                if ('ME' in c):
                    exhaustids.append(self.nctrl)
                else:
                    supplyids.append(self.nctrl)
                    

        for d in exhaustids:
            
            if (exhaustids.index(d)==0):
                previous=d
                continue

            self.addBasicOperation('add','<none>',previous,d)
            #print("Den: Previous,current,new",previous,d,self.nctrl)
            previous=self.nctrl
            

        totaleid=self.nctrl
      
        for d in supplyids:
            
            if (supplyids.index(d)==0):
                previous=d
                continue

            self.addBasicOperation('add','<none>',previous,d)
            #print("Den: Previous,current,new",previous,d,self.nctrl)
            previous=self.nctrl
            

        totalsid=self.nctrl
      
        supoverexh=self.addBasicOperation('div','<none>',totalsid,totaleid)
        
        self.addreport(supoverexh,'Sup_over_exh')
        #I checked it wrt log, it works at the first try!!! too strong :-) 

        c1=self.addconstant('<none>',1)
        soeswitch=self.addULS(supoverexh,c1) # sup/exh > 1       
        inverse=self.addNot(soeswitch)

        #soemin=self.addMinMax('max','<none>',[soeswith,self.addconstant('<none>',0.01)])

        supcase1=self.addBasicOperation('mul','<none>',c1,soeswitch)
        supcase2=self.addBasicOperation('div','<none>',inverse,supoverexh)
        fsup=self.addMinMax('max','<none>',[supcase1,supcase2])
        
        exhcase1=self.addBasicOperation('mul','<none>',soeswitch,supoverexh)
        exhcase2=self.addBasicOperation('mul','<none>',inverse,c1)
        fexh=self.addMinMax('max','<none>',[exhcase1,exhcase2])

        # This has been checked, it works!)
        #self.addreport(fsup,'fsup')
        #self.addreport(fexh,'fexh')
        
        returndict={}
        
        
        for c in unbal_ctrls_dict.keys():
            room=c.split('_')[-1]

            if (room in balrooms) or (room in shortrooms):

                if ('ME' in c):
                    mult=fexh
                if ('MS' in c):
                    mult=fsup

                cid=ids[unbal_ctrls_dict[c]]
                returndict[c]=self.addBasicOperation('mul','<none>',mult,cid)
                
        
        return(returndict)

    def addGlobalExtractMinimumControlOnTopOfLocal(self,extractRooms,nom_flows_dict,local_ctrls_dict,globalMinimumCtrlId,ids):
    
        #print(nom_flows_dict)
        #print(unbal_ctrls_dict)
        #print(ids)
        
        #print(balrooms)
        shortrooms=[x.replace('kamer','') for x in extractRooms]

        supplyids=[]
        exhaustids=[]

        qtot = 0
        
        for c in local_ctrls_dict.keys():

            room=c.split('_')[-1]

            if (room in extractRooms) or (room in shortrooms):

                qnom=nom_flows_dict[c]

                qtot += qnom

                self.addconstant('<none>',qnom)
                
                qid=self.nctrl
                cid=ids[local_ctrls_dict[c]]
                
                #print(qid,cid)
                self.addBasicOperation('mul','<none>',qid,cid,'')

                if ('ME' in c):
                    exhaustids.append(self.nctrl)
                #else:
                #    supplyids.append(self.nctrl)
                    


        for d in exhaustids:
            
            if (exhaustids.index(d)==0):
                previous=d
                continue

            self.addBasicOperation('add','<none>',previous,d)
            #print("Den: Previous,current,new",previous,d,self.nctrl)
            previous=self.nctrl
            

        totaleid=self.nctrl

        
        for d in supplyids:
            
            if (supplyids.index(d)==0):
                previous=d
                continue

            self.addBasicOperation('add','<none>',previous,d)
            #print("Den: Previous,current,new",previous,d,self.nctrl)
            previous=self.nctrl
            

        #total Nominal extract flow
        self.addconstant('<none>',qtot) 
        totalNominalExtractFlowId = self.nctrl

        #total nominal flow * control variable for the gloal control
        self.addBasicOperation('mul','<none>',totalNominalExtractFlowId,globalMinimumCtrlId ,'')
        totalsid=self.nctrl

        
        supoverexh=self.addBasicOperation('div','<none>',totalsid,totaleid)
        
        self.addreport(supoverexh,'Sup_over_exh')
        #I checked it wrt log, it works at the first try!!! too strong :-) 

        c1=self.addconstant('<none>',1)
        soeswitch=self.addULS(supoverexh,c1) # sup/exh > 1       
        inverse=self.addNot(soeswitch)

        #soemin=self.addMinMax('max','<none>',[soeswith,self.addconstant('<none>',0.01)])

        #supcase1=self.addBasicOperation('mul','<none>',c1,soeswitch)
        #supcase2=self.addBasicOperation('div','<none>',inverse,supoverexh)
        #fsup=self.addMinMax('max','<none>',[supcase1,supcase2])
        
        exhcase1=self.addBasicOperation('mul','<none>',soeswitch,supoverexh)
        exhcase2=self.addBasicOperation('mul','<none>',inverse,c1)
        fexh=self.addMinMax('max','<none>',[exhcase1,exhcase2])

        
        returndict={}
        
        
        for c in local_ctrls_dict.keys():
            room=c.split('_')[-1]

            if (room in extractRooms) or (room in shortrooms):

                if ('ME' in c):
                    mult=fexh
                #if ('MS' in c):
                #    mult=fsup not sup here, its juste a set point for minimum global extract

                cid=ids[local_ctrls_dict[c]]
                returndict[c]=self.addBasicOperation('mul','<none>',mult,cid)
                
        
        return(returndict)

        
    def addNot(self,inputvalue,name='',description=''):
    
        self.nctrl+=1
        self.df.loc[self.nctrl,'typ']='inv'
        self.df.loc[self.nctrl,'seq']=int(self.nctrl)
        self.df.loc[self.nctrl,'f']=int(0)
        self.df.loc[self.nctrl,'n']=int(1)
        self.df.loc[self.nctrl,'c1']=int(inputvalue)
        self.df.loc[self.nctrl,'c2']=int(0)
        self.df.loc[self.nctrl,'name']=name

        if (description==''):
            description='uls by Python'
        else:
            description+=' - by Python'
        self.df.loc[self.nctrl,'description']=description
    
        self.df.at[self.nctrl,'values']=[ ]
        
        return self.nctrl
    
        
    def addULS(self,inputvalue,limit,name='',description=''):
    
        self.nctrl+=1
        self.df.loc[self.nctrl,'typ']='uls'
        self.df.loc[self.nctrl,'seq']=int(self.nctrl)
        self.df.loc[self.nctrl,'f']=int(0)
        self.df.loc[self.nctrl,'n']=int(2)
        self.df.loc[self.nctrl,'c1']=int(inputvalue)
        self.df.loc[self.nctrl,'c2']=int(limit)
        self.df.loc[self.nctrl,'name']=name
        
        
        if (description==''):
            description='uls by Python'
        else:
            description+=' - by Python'
        self.df.loc[self.nctrl,'description']=description
    
        self.df.at[self.nctrl,'values']=[ ]
    
        return self.nctrl

    def addLLS(self,inputvalue,limit,name='',description=''):
    
        self.nctrl+=1
        self.df.loc[self.nctrl,'typ']='lls'
        self.df.loc[self.nctrl,'seq']=int(self.nctrl)
        self.df.loc[self.nctrl,'f']=int(0)
        self.df.loc[self.nctrl,'n']=int(2)
        self.df.loc[self.nctrl,'c1']=int(inputvalue)
        self.df.loc[self.nctrl,'c2']=int(limit)
        self.df.loc[self.nctrl,'name']=name
        
        
        if (description==''):
            description='lower limit switch by Python'
        else:
            description+=' - by Python'
        self.df.loc[self.nctrl,'description']=description
    
        self.df.at[self.nctrl,'values']=[ ]
    
        return self.nctrl


    def addPresenceSensor(self,roomname,occupancy_id,name=''):
  
        self.addconstant('one',1)
        cid=self.nctrl
        self.addMinMax('min','P_'+roomname,[cid,occupancy_id])
        
        #print("added presence in code",self.nctrl)
        #self.addreport(self.nctrl,'presenceWC',reporttype='',description='')

        
        return self.nctrl

    def addScheduleControl(self,weekschedule,name='',description=''):
    
        if (name==''):
            name='<none>'
    
        self.nctrl+=1
        self.df.loc[self.nctrl,'typ']='sch'
        self.df.loc[self.nctrl,'seq']=int(self.nctrl)
        self.df.loc[self.nctrl,'f']=int(0)
        self.df.loc[self.nctrl,'n']=int(0)
        self.df.loc[self.nctrl,'c1']=int(0)
        self.df.loc[self.nctrl,'c2']=int(0)
        self.df.loc[self.nctrl,'name']=name

        if (description==''):
            description='schedule by Python'
        else:
            description+=' - by Python'
        self.df.loc[self.nctrl,'description']=description
    
        self.df.at[self.nctrl,'values']=[weekschedule]
        
        return self.nctrl
        

    def addScheduledDelay(self,inputsignalid,scheduleup,scheduledown):
    
        description=''
    
        #! # typ seq f n  c1  c2 name
        #1 dls   3 0 1   4   0 DelayControl
        #Delay input by schedule
        self.nctrl+=1
        self.df.loc[self.nctrl,'typ']='dls'
        self.df.loc[self.nctrl,'seq']=int(self.nctrl)
        self.df.loc[self.nctrl,'f']=int(0)
        self.df.loc[self.nctrl,'n']=int(1)
        self.df.loc[self.nctrl,'c1']=int(inputsignalid)
        self.df.loc[self.nctrl,'c2']=int(0)
        self.df.loc[self.nctrl,'name']='DelayControl'

        if (description==''):
            description='Delay input by schedule'
        else:
            description+=' - by Python'
        self.df.loc[self.nctrl,'description']=description
    
        self.df.at[self.nctrl,'values']=[scheduleup,scheduledown]
        
        return self.nctrl

    def addClockControl(self,schedules,weekschedules,clockschedule,name=''):
   
        clockdf=pd.DataFrame( [ [h,v] for h,v in clockschedule.items() ] )
        clockdf.columns=['hour','value']
        
        schedules.addSchedule(name,'Clock control by Python',clockdf,shape=0) #day schedule! 
 
        list_of_day_schedules=[ schedules.nschedules for i in range(12) ]
 
        weekschedules.addSchedule('W'+name,'Week schedule for clock control',list_of_day_schedules)
        
        ctrlid=self.addScheduleControl(weekschedules.nschedules,'ScControl','Schedule control for '+name)
        
        return ctrlid

        

    def addTimerControl(self,schedules,signalid,qmin,qmax,duration,name=''):


        #detection: instantaneous (or close)
        updf=pd.DataFrame([['00:00:00',0],['00:00:01',1],['24:00:00',1]])
        updf.columns=['hour','value']

        #stop: timer 
        
        if ( ('min' not in duration) and ('h' not in duration) and ('H' not in duration)):
            print("Invalid time format")
            print("Use  only 'min', 'h' or 'H', like '1H', '30min', '3h'")
        else:
            stringduration=convertTimeString(duration)
            stringduration2=stringduration[0:6]+'01'

        downdf=pd.DataFrame([['00:00:00',1],[stringduration,1],[stringduration2,0],['24:00:00',0]])
        downdf.columns=['hour','value']

        schedules.addSchedule('up','instantaneous raise',updf,shape=1)
        upid=schedules.nschedules
        schedules.addSchedule('down','fall after 30 min',downdf,shape=1)
        downid=schedules.nschedules

        #print("added schedules")

        ctrlids={}

        '''
        formule :  
        
        signal  = max ( delay(presence) * qmax  , qmin)
        
        si presence = 1  --> qmax
        si presence = 0 --> max (0,qmin) --> qmin
        '''

        self.addconstant('Qmin',qmin)
        ctrlids['Qmin']=self.nctrl
        self.addconstant('Qmax',qmax)
        ctrlids['Qmax']=self.nctrl
   
        scheduleddelay=self.addScheduledDelay(signalid,upid,downid) 

        #self.addreport(scheduleddelay,'delayWC',reporttype='',description='')
        
        delaytimeqmax=self.addBasicOperation('mul','<none>',ctrlids['Qmax'],scheduleddelay)      
        finalid=self.addMinMax('max','Final',[ctrlids['Qmin'],delaytimeqmax])
  
        #print("Addeed final",finalid)
        #self.addreport(finalid,'reportWC',reporttype='',description='')

  
        return finalid

    
    def addSourceLimiter(self,roomname,weekschedule):
        #stop source if RH > 100
        
        constant1=self.addconstant('1',1)
        sensor_name='H2O_'+roomname
        sensor_id=self.df[self.df['name']==sensor_name].index[0]
         
        
         
        switch=self.addLLS(sensor_id,constant1,name='LLS',description='Lower limit switch for H2O in '+roomname)
        schedule=self.addScheduleControl(weekschedule)

        sourcecontrol=self.addBasicOperation('mul','<none>',switch,schedule)

        #self.addreport(sourcecontrol,'reportSource'+roomname,reporttype='',description='')


        return sourcecontrol
        
    
    def addSum(self,name,ctrlidstosumaslist,description):
        
            nids = len(ctrlidstosumaslist)
        
            self.nctrl+=1
            self.df.loc[self.nctrl,'typ']='sum'
            self.df.loc[self.nctrl,'seq']=int(self.nctrl)
            self.df.loc[self.nctrl,'f']=int(0)
            self.df.loc[self.nctrl,'n']=nids
            self.df.loc[self.nctrl,'c1']=0
            self.df.loc[self.nctrl,'c2']=0
            self.df.loc[self.nctrl,'name']=name
            
            
            if (description==''):
                description='sum by Python'
            else:
                description+=' - by Python'
            self.df.loc[self.nctrl,'description']=description
        
            values = [nids]+ctrlidstosumaslist
        
            self.df.at[self.nctrl,'values']=values
        
            return self.nctrl
     
        
    
    def addWeightedSum(self,signals_ids,weights):
        
        weight_ids = []


        numeratorterms =[]

        
        for w in weights:
            wid=self.addconstant('weight'+str(w),w)
            weight_ids.append(wid)
            
            
        for wid,sid in zip(weight_ids,signals_ids):
            
            weightedSignal =self.addBasicOperation('mul','<none>',wid,sid)      
            numeratorterms.append(weightedSignal)


        numeratorid = self.addSum('num_sum',numeratorterms,'numerator for weighted sum')
        denominatorid = self.addSum('den_sum',weight_ids,'denotminator for wweighted sum')

        weightedsignal = self.addBasicOperation('div', 'weightedsign', numeratorid, denominatorid)            

        self.addreport(weightedsignal,'C_Wei_'+str(weightedsignal))



        return weightedsignal            
        
        
class occupancy_schedules:

    # The occupancy schedule section starts with:
    # _nosch // number of schedules (IX)
    # This is followed by a data header comment line and then data for all _nosch schedules.
    # For each schedule the first data line includes:
    # nr // schedule number (IX); in order from 1 to _nosch
    # npts // number of points (I2)
    # u_XYZ // units of location coordinates (I2)
    # name[] // schedule name (I1) {W}
    # and the second line has:
    # desc[] // schedule description (I1) {W} may be blank
    # This is followed by npts lines of schedule data:
    # time // time-of-day [s] (hh:mm:ss converted to I4)
    # pz // zone index (I2); converted to pointer
    # X // X-coordinate of occupant [m] (R4)
    # Y // Y-coordinate of occupant [m] (R4)
    # relHt // height relative to current level [m] (R4)

    def __init__(self):
        self.nschedules=0
        self.comment=' occupancy schedules'
        self.schedules={} #schedules by contam ID

        
        # 1 sechedule  
        # {'id':id,'name':name,'description':description,'dataframe':dataframe}
        
    def read(self,filereader,currentline):
    
        nschedules,self.comment = currentline.split('!')
        self.nschedules=int(nschedules)
        
        for i in range(self.nschedules):
        
            sdict={}
        
            fields=filereader.readline().split()

            sid=int(fields[0])
            
            #sdict[s]=int(fields[0])
            npoints=int(fields[1])
            #fields 2 is 0
            sdict['name']=fields[3]
            sdict['description']=filereader.readline()

            cols=['hour','zid','x','y','relHt']
            sdict['dataframe']=pd.DataFrame(columns=cols)
            
            for l in range(npoints):
                fields=filereader.readline().split()
                sdict['dataframe']=sdict['dataframe'].append(dict(zip(cols,fields)),ignore_index=True)

            

            sdict['dataframe']=convert_cols(sdict['dataframe'])

            self.schedules[sid]=sdict
            
    def write(self,g):
        
        g.write(str(self.nschedules)+' !'+self.comment)

        for k,v in self.schedules.items():
        
            line1=str(k)
            line1=line1+' '+str(len(v['dataframe']))+' 0 '+v['name']+'\n'
            g.write(line1)
            g.write(v['description'])
            
            if ('\n' not in v['description']):
                g.write('\n')
            
            
            if 'shower' in v['dataframe'].columns:
                v['dataframe'].drop(['shower'],axis=1).to_csv(g,header=False,index=False,sep=' ',line_terminator='\n')

            else:
                v['dataframe'].to_csv(g,header=False,index=False,sep=' ',line_terminator='\n')
            

    def addSchedule(self,name,description,profiledf):
    
        #profile df: one expect only hours and numbers columns: 'hour','zid'
        
        if ('hour' not in list(profiledf.columns) or 'zid' not in list(profiledf.columns)):
            print("Hour and zid should be in the columns")
            return
        
        
        newid=self.nschedules+1
        sdict={}
          
        npoints=len(profiledf)
        sdict['name']=name
        sdict['description']=description

        sdict['dataframe']=profiledf.loc[:,['hour','zid','shower']]
        sdict['dataframe']['x']=0.0
        sdict['dataframe']['y']=0.0
        sdict['dataframe']['relHt']=0.0
                
        
        self.schedules[newid]=sdict
        
        self.nschedules+=1

        return

    def getLastId(self):
        return np.max(list(self.schedules.keys()))

    def genEmissionSchedule(self,occupancyScheduleID,bedroomID,fraction):
        # Generate a day-schedule with "fraction" value during the night, but 1 during the day
        # The schedule is based on a true occupancy schedule and the bedroomID
        # If the occupant is in its bedroom, then fraction is applied
        # Else: the emission rate is 1

        # returns a df with ['hour','mult'] columns
        # this is not returning a full day-schedule in contam format
        # this should be done in a "day-schedule" class
        
        
        edf=pd.DataFrame()
        odf=self.schedules[occupancyScheduleID]['dataframe']
        edf['hour']=odf['hour']
        x= [ fraction if odf.loc[i,'zid']==bedroomID else 1.0 for i in odf.index ]
        edf['value']=x
        
        return(edf)
    

class daySchedules:

    # The day schedules section starts with:
    # _ndsch // number of day schedules (IX)
    # This is followed by a data header comment line and then data for all _ndsch schedules.
    # For each schedule the first data line includes:
    # nr // schedule number (IX); in order from 1 to _ndsch
    # npts // number of data points (I2)
    # shape // 0 = rectangular; 1 = trapezoidal (I2)
    # utyp // type of units (I2) {W}
    # ucnv // units conversion (I2) {W}
    # name[] // schedule name (I1) {W}
    # and the second line has:
    # desc[] // schedule description (I1) {W} may be blank
    # This is followed by a line for each of the npts data points:
    # time // time-of-day [s] (hh:mm:ss converted to I4)
    # ctrl // corresponding control value (R4) [-]
    # The section is terminated with:
    # -999 // used to check for a read error in the above data

    # 1    8    0    1    0 Dag_Geur_O1
    # Geurproductie tijdens aanwezigheid wc
    # 00:00:00 0
    # 07:25:00 1
    # 07:30:00 0
    # 15:10:00 1
    # 15:15:00 0
    # 22:55:00 1
    # 23:00:00 0
    # 24:00:00 0


    def __init__(self):
        self.nschedules=0
        self.comment=' day schedules'
        self.schedules={} #schedules by contam ID
        
    def read(self,filereader,currentline):
    
        nschedules,self.comment = currentline.split('!')
        self.nschedules=int(nschedules)
        
        for i in range(self.nschedules):
        
            sdict={}
        
            fields=filereader.readline().split()
            
            if (fields[0] == '!'):
                #in case of header --> it seems CONTAMW write it, while it is ignored up to now when I generate myself
                # temporary trick= I repead the readline...
                fields=filereader.readline().split()

            sid=int(fields[0])
            npoints=int(fields[1])
            sdict['shape']=int(fields[2])
            #fields 2 3 4 are 0 1 0
            sdict['name']=fields[5]
            sdict['description']=filereader.readline()

            cols=['hour','value']
            sdict['dataframe']=pd.DataFrame(columns=cols)
            
            
            
            for l in range(npoints):
                fields=filereader.readline().split()
                
                dictToAppend = dict(zip(cols,fields))
                sdict['dataframe'] = pd.concat( [sdict['dataframe'],pd.DataFrame.from_records(dictToAppend,index=[0]) ],ignore_index=True)                
                #sdict['dataframe']=sdict['dataframe'].append(dict(zip(cols,fields)),ignore_index=True)

            

            sdict['dataframe']=convert_cols(sdict['dataframe'])

            self.schedules[sid]=sdict
            
    def write(self,g):
        
        g.write(str(self.nschedules)+' !'+self.comment)

        for k,v in self.schedules.items():
        
            line1=str(k)
            line1=line1+' '+str(len(v['dataframe']))+' '+str(v['shape'])+' 1 0 '+v['name']+'\n'
            g.write(line1)
            g.write(v['description'])
            
            if ('\n' not in v['description']):
                g.write('\n')
            
            v['dataframe'].to_csv(g,header=False,index=False,sep=' ',line_terminator='\n')
            

    def addSchedule(self,name,description,profiledf,shape=0):
    
        #profile df: one expect only hours and numbers columns: 'hour','zid'
        
        if ('hour' not in list(profiledf.columns) or 'value' not in list(profiledf.columns)):
            print("Hour and value should be in the columns")
            return
        
        newid=self.nschedules+1
        sdict={}
          
        npoints=len(profiledf)
        sdict['name']=name
        sdict['description']=description
        sdict['dataframe']=profiledf.loc[:,['hour','value']]
        sdict['shape']=shape
 

        self.schedules[newid]=sdict
        self.nschedules+=1

        return

    def getLastId(self):
        return np.max(list(self.schedules.keys()))


class weekSchedules:

    # _nwsch // number of week schedules (IX)
    # This is followed by a data header comment line and then data for all _nwsch schedules.
    # For each week schedule the first data line includes:
    # nr // schedule number (IX); in order from 1 to _nwsch
    # utyp // type of units (I2) {W}
    # ucnv // units conversion (I2) {W}
    # name[] // schedule name (I1) {W}
    # and the second line has:
    # desc[] // schedule description (I1) {W} may be blank
    # and the third line has:
    # j1 … j12 // 12 day schedule indices (IX) – converted to pointers

    def __init__(self):
        self.nschedules=0
        self.comment='week-schedules'
        self.schedules={} #schedules by contam ID id:[list]
        self.nschedules=0
        self.headerline="! # utype uconv name\n"
 
    def read(self,filereader,currentline):
    
        nschedules,self.comment = currentline.split('!')
        self.nschedules=int(nschedules)

        nextline=filereader.readline()
        if(nextline[0] == '!' ):
            self.headerline=nextline
        
        for i in range(self.nschedules):
        
            sdict={}
        
            fields=filereader.readline().split()
                
            nr=int(fields[0])
            utype=fields[1]
            uconv=fields[2]
            name=fields[3]
            
            description=filereader.readline()
            days_schedules=filereader.readline().split()

            sdict={'utype':utype,'uconv':uconv,'name':name,'description':description,'days_schedules':days_schedules}
            
            self.schedules[nr]=sdict
    
        self.nschedules=len(self.schedules)


    def write(self,g):
    
        
        g.write(str(self.nschedules)+' ! '+self.comment)
        if ('\n' not in self.comment):
            g.write('\n')
        g.write(self.headerline)
        for k,v in self.schedules.items():
        
            g.write(str(k)+' '+v['utype']+' '+v['uconv']+' '+v['name']+'\n')
            g.write(v['description'])
            
            if ('\n' not in v['description']):
                g.write('\n')
            
            schedulestring=''
            for s in v['days_schedules']:
                schedulestring+=' '
                schedulestring+=str(s)
            
            g.write(schedulestring+'\n')
          
    def addSchedule(self,name,description,dayschedules):
    
        newid=self.nschedules+1
        sdict={}
          
        sdict['utype']='1'
        sdict['uconv']='0'
        sdict['name']=name
        sdict['description']=description
        sdict['days_schedules']=dayschedules
        
        self.schedules[newid]=sdict
        self.nschedules+=1

        return
            
    
    def getLastId(self):
    
        return np.max(list(self.schedules.keys()))
    

class exposures:

    # The exposure section starts with:
    # _npexp // number of exposures (IX)
    
    # This is followed by three lines of data for all _npexp exposures.
    # For each exposure the first data line includes:
    # nr // exposure number (IX); in order from 1 to _npexp
    # gen // = 1 if contaminants are generated (I2)
    # ncg // number of contaminant generations (I2)
    # cgmlt // contaminant generation multiplier [-] (R4)
    # color // icon color (I2) {W} {CONTAM 3.3} NEW
    
    # The second line has the exposure description:
    # desc[] // exposure/person description (I1)
    # The third line has the indices of 12 occupancy schedules:
    # odsch[12] // vector of daily occupancy schedules – 12 indices
    # It is followed by ncg lines of contaminant generation data:
    # name // species name (I1)
    # Appendix A - PRJ File Format
    # 308
    # ps // schedule index (I2); converted to pointer
    # cgmax // peak generation rate [kg/s] (R4)
    # u_cg // units of generation rate (I2) {W}
    # vf_type // 0=no value file, 1=use cvf, 2=use dvf (I2) {CONTAM 3.2}
    # If vf_type > 0 then the line continues to include:
    # vf_node_name[NAMELEN] // value file node name (I1) {CONTAM 3.2}
    # The exposure section is terminated with:
    # -999 // used to check for a read error in the above data

    def __init__(self):
        self.nexposures=0
        self.comment='exposures'
        self.exposures={} #schedules by contam ID id:[list]
        self.nexposures=0
 
    def read(self,filereader,currentline):
    
        nexposures,self.comment = currentline.split('!')
        self.nexposures=int(nexposures)

        
        for i in range(self.nexposures):
        
            sdict={}
        
            fields=filereader.readline().split()
                
            nr=int(fields[0])
            gencontaminants=fields[1]
            ncontaminants=int(fields[2])
            multiplier=fields[3]
            color = fields[4]
            
            description=filereader.readline()

            days_schedules,comment=filereader.readline().split('!')
            days_schedules=[ int(x) for x in days_schedules.split() ]
            
            sdict['day_schedules']=days_schedules
            sdict['gencontaminants']=gencontaminants
            sdict['ncontaminants']=ncontaminants
            sdict['multiplier']=multiplier
            sdict['color']=color
            
            sdict['description']=description
            sdict['CTMemission']=[]


            
            for c in range(ncontaminants):
                cdict={}
                data,comment=filereader.readline().split('!')
                name,schedule,gen_rate,unit,value_file = data.split()
                cdict={'name':name,'schedule':schedule,'rate':gen_rate,'unit':unit,'value_file':value_file}

                sdict['CTMemission'].append(cdict)
            
            self.exposures[nr]=sdict

    def write(self,g):
        
        g.write(str(self.nexposures)+' ! '+self.comment)
        if ('\n' not in self.comment):
            g.write('\n')

        

        for k,v in self.exposures.items():

            g.write(str(k)+' '+str(v['gencontaminants'])+' '+str(v['ncontaminants'])+' '+str(v['multiplier'])+' '+str(v['color'])+'\n')

            g.write(v['description'])
            if ('\n' not in v['description']):
                g.write('\n')

            [ g.write(str(x)+' ') for x in v['day_schedules'] ]
            g.write(' ! occ. sched \n')

            
            for item in v['CTMemission']:
                g.write(item['name']+' '+str(item['schedule'])+' '+str(item['rate'])+' '+str(item['unit'])+' '+str(item['value_file'])+' ! occ. gen\n')
            
        
    def addExposure(self,description,occupancy_week_schedule,ctmdictlist,color='-1'):
    
        newid=self.nexposures+1
        sdict={}

        sdict['day_schedules']=occupancy_week_schedule
                    
        sdict['gencontaminants']='1'
        sdict['ncontaminants']=len(ctmdictlist)
        sdict['multiplier']='1'
        sdict['description']=description
        sdict['color']=color

          
        sdict['CTMemission']=ctmdictlist # {name:  ; schedule:  ,'rate':  ,'unit':  , value_file = 0 }
        
        
        #{'name':'CO2','schedule':co2Wid,'rate':16,'unit':'L/h','value_file':0},
        #{'name':'H2O','schedule':h2oWid,'rate':55,'unit':'g/h','value_file':0}

        RefVolume= 24.055 # 1 mole = 22,4 l at 0 deg C  or 24.055 at 20 deg C
        MMdict={'CO2':44,'H2O':18}

        for speciesDict in sdict['CTMemission']:
        
        
            if speciesDict['unit']=='L/h':
                rate=MMdict[speciesDict['name']]*speciesDict['rate']/RefVolume/3600/1000
                unit=33
            
            elif speciesDict['unit']=='g/h':
                rate=speciesDict['rate']/1000/3600
                unit=28
        
            speciesDict['rate']=rate
            speciesDict['unit']=unit
        
        self.exposures[newid]=sdict
        self.nexposures+=1

        return
            
    
    def getLastId(self):
    
        return np.max(list(self.exposures.keys()))
    

class flowpaths:

    # nr // path number (IX); in order from 1 to _npath
    # flags // airflow path flag values (I2)
    # pzn // zone N index (IX); converted to pointer
    # pzm // zone M index (IX);to pointer
    # pe // flow element index (IX); converted to pointer
    # pf // filter index (IX); converted to pointer
    # pw // wind coefficients index (IX); converted to pointer
    # pa // AHS index (IX); converted to pointer
    # ps // schedule index (IX); converted to pointer
    # pc // control node index (IX); converted to pointer
    # pld // level index (IX); converted to pointer
    # X // X-coordinate of envelope path [m] (R4) {Contam 2.1}
    # Y // Y-coordinate of envelope path [m] (R4) {Contam 2.1}
    # relHt // height relative to current level [m] (R4)
    # mult // element multiplier (R4)
    # wPset // constant wind pressure [Pa] (pw==NULL) (R4)
    # wPmod // wind speed(?) modifier (pw!=NULL) (R4)
    # wazm // wall azimuth angle (pw!=NULL) (R4)
    # Fahs // AHS path flow rate [kg/s] (pw==NULL) (R4)
    # Xmax // flow or pressure limit - maximum (R4) {W}
    # Xmin // flow or pressure limit - minimum (R4) {W}
    # icon // icon used to represent flow path (U1) {W}
    # dir // positive flow direction on sketchpad (U1) {W}
    # color // NEW FROM 3.3
    # u_Ht // units of height (I2) {W}
    # u_XY // units of X and Y (I2) {W}
    # u_dP // units of pressure difference (I2) {W}
    # u_F // units of flow (I2) {W}
    # vf_type // 0=no value file, 1=use cvf, 2=use dvf (I2) {CONTAM 3.2}
    # vf_node_name[NAMELEN] // value file node name (I1) {CONTAM 3.2}
    # cfd // cfd path (0=no, 1=yes) (I2) {CONTAM 3.0}
    # If cfd = 1 then the line continues to include: {CONTAM 3.0}
    # name[] // cfd path id (I1)
    # cfd_ptype // boundary condition type (0=mass flow, 1=pressure) (I2)
    # cfd_btype // pressure bc type (if ptype = 1, 0=linear, 1=stagnation pressure) (I2)
    # cfd_capp // coupling approach (1=pressure-pressure) (I2)

    def __init__(self):
        
        self.headers=['nr','flags','pzn','pzm','pe','pf','pw','pa','ps','pc','pld','X','Y','relHt',
        'mult','wPset','wPmod','wazm','Fahs','Xmax','Xmin','icon','dir','color','u_Ht','u_XY','u_dP','u_F',
        'vf_type','vf_node_name','cfd','name','cfd_ptype','cfd_btype','cfd_capp'] 

        self.df=pd.DataFrame(columns=self.headers)
        
    
    def readCONTAMfp(self,filereader,currentline):
        
        nfp,self.comment=currentline.split('!')
        self.nfp=int(nfp)
        self.contamheader=filereader.readline() #headers

        for i in range(self.nfp):
            fields=filereader.readline().split()
            mydict={self.headers[i]:fields[i] for i in range(len(fields))}
    
            if mydict['vf_type']=='0':
                mydict['cfd']=mydict['vf_node_name']
                mydict['vf_node_name']=''


            #self.df = pd.concat([self.df,pd.DataFrame.from_records([mydict])])
            self.df = pd.concat([self.df,pd.DataFrame.from_records([mydict])])
            
         
        self.df.index=self.df['nr'].astype(int)
        self.df.drop(['nr'],axis=1,inplace=True)
        self.df=convert_cols(self.df)


    def writeCONTAMfp(self,g):
        
        g.write(str(self.nfp)+' !'+self.comment)
        g.write(self.contamheader)
        self.df.to_csv(g,header=False,sep=' ',line_terminator='\n')
        

class windpressureprofiles:

    #_nwpf // number of wind pressure profiles (IX)

    #nr // profile number (IX); in order from 1 to _nwpf
    #npts // number of data points (I2)
    #type // 1 = linear; 2 = cubic spline; 3 = trigonometric (I2)
    #name[]
    
    # + header
    # azm coeff

    def __init__(self):
        
        self.nprofiles=0
        self.headers=['nr','npts','type','name','comment','values'] 
        self.df=pd.DataFrame(columns=self.headers)

    def read(self,filereader,currentline):
    
        self.nprofiles,self.comment = currentline.split('!')
        self.nprofiles=int(self.nprofiles)

        for i in range(self.nprofiles):
            
            fields=filereader.readline().split()

            tmpdict = dict(zip(self.headers,fields))
           
            self.df = pd.concat([self.df,pd.DataFrame.from_records([tmpdict])],ignore_index=True)
                       
            
            self.df.loc[i,'comment']=filereader.readline()
            self.df.at[i,'values']=[]
            
            for point in range(int(self.df.loc[i,'npts'])):
                self.df.loc[i,'values'].append(filereader.readline().split())

        self.df.index=self.df['nr'].astype(int)
        self.df.drop(['nr'],axis=1,inplace=True)
        self.df=convert_cols(self.df)
              
        
    def write(self,g):
    
        g.write(str(self.nprofiles)+' ! '+self.comment)
        for i in range(self.nprofiles):
            
            index=self.df.index[i]
            
            g.write(str(index)+' ')
            [g.write(str(self.df.loc[index,col])+' ') for col in ['npts','type','name']]
            g.write('\n')
            g.write(self.df.loc[index,'comment'])
            
            for pair in self.df.loc[index,'values']:
                g.write(pair[0]+' '+pair[1]+'\n')
                
        return
    
    def add(self,otherdf):
    
        self.nprofiles = self.nprofiles+len(otherdf)
    
        self.df = self.df.append(otherdf,ignore_index = True)
        self.df.index = [ i+1 for i in range(self.nprofiles)]
    
        return
    
    def replaceFromLibrary(self,librarydf):
    
        self.nprofiles = len(librarydf)
        self.df = librarydf
    
        return
    
    

class SimInputs:
    def read(self,filereader,currentline):

        self.otherlines=[]
        
        self.saveflags=[] #list of dicts
        
        lastline=''
        
        self.otherlines.append(currentline)
        
        while('-999' not in lastline):
            lastline=filereader.readline()
            
            
            if ('sim_af' in lastline):
                self.otherlines.append(lastline)
                fields = filereader.readline().split()
                self.airFlowsParameters = fields
                continue

            if ('sim_mf' in lastline):
                self.otherlines.append(lastline)
                fields = filereader.readline().split()
                self.massFractionParameters = fields
                continue


            if ('weather file' in lastline):
                self.weatherfile,self.wcomment=lastline.split('!')
                self.otherlines.append(lastline)  #je sauve la ligne tel quel, mais modifiee dynamiquement a l'ecriture
                continue

            if ('contaminant file' in lastline):
                self.contaminantfile,self.contaminantcomment=lastline.split('!')
                self.otherlines.append(lastline)  #je sauve la ligne tel quel, mais modifiee dynamiquement a l'ecriture
                continue

                
            if ('!date_st' in lastline):
                self.otherlines.append(lastline)  #je sauve cette ligne pour la reecrire tel quel
                headers=lastline.split() #headers as list
                times=filereader.readline().split()
                # dates and time as list - pas sauve, sera reecrit dynamiquemnet
                
                self.times={h:t for h,t in zip(headers,times)}
                continue
             
            if ('doDlg' in lastline):
                    
                self.otherlines.append(lastline)  #je sauve cette ligne pour la reecrire tel quel
                headers=lastline.split() #headers as list
                flags=filereader.readline().split()
                # dates and time as list - pas sauve, sera reecrit dynamiquemnet
                
                self.saveflags.append({h:t for h,t in zip(headers,flags)})
                continue
             
            if ('!vol' in lastline):
                    
                self.otherlines.append(lastline)  #je sauve cette ligne pour la reecrire tel quel
                headers=lastline.split() #headers as list
                flags=filereader.readline().split()
                # dates and time as list - pas sauve, sera reecrit dynamiquemnet
                
                for hi in range(len(headers)):
                    if headers[hi]=='-bw':
                        headers[hi]=headers[hi-1]+headers[hi]
                
                
                self.saveflags.append({h:t for h,t in zip(headers,flags)})
                continue

            if ('!rzf' in lastline):
                    
                self.otherlines.append(lastline)  #je sauve cette ligne pour la reecrire tel quel
                headers=lastline.split() #headers as list
                flags=filereader.readline().split()
                # dates and time as list - pas sauve, sera reecrit dynamiquemnet
                
                self.saveflags.append({h:t for h,t in zip(headers,flags)})
                continue

            
            self.otherlines.append(lastline)
                

        self.otherlines.remove(self.otherlines[-1])
        
        
        return

    def setdefaultstimes(self):
    
        self.settimestep('00:05:00')
        self.setoutputfreq('00:05:00')
        self.setstartend('Jan01','Dec31')
        self.times['t_scrn']='24:00:00'
        
    def setweather(self,weatherfilepath):
    
        self.weatherfile=weatherfilepath

    def setcontaminantFile(self,contaminantsfilepath):
    
        self.contaminantfile = contaminantsfilepath


    def setoutputfreq(self,freq):
    
        #format HH:MM:SS
        self.times['t_list']=freq

    def settimestep(self,timestep):
    
        #format HH:MM:SS
        self.times['t_step']=timestep

    def setstartend(self,startdate,enddate):
    
        #fora Jan01 Feb01, ... Nov30, Dec31
    
        self.times['date_0']=startdate
        self.times['date_1']=enddate
        
    
    def setoutputs(self,outputslist):
    
        alloutputs=['simflow','simconc','log','ach','ebw']
        
        if 'simflow' in outputslist:
            self.saveflags[0]['pfsave']='1'
            self.saveflags[0]['zfsave']='1'
        else:
            self.saveflags[0]['pfsave']='0'
            self.saveflags[0]['zfsave']='0'
            
        if 'simconc' in outputslist:
            self.saveflags[0]['zcsave']='1'
        else:
            self.saveflags[0]['zcsave']='0'
        
        if 'ach' in outputslist:
            self.saveflags[1]['ach']='1'
        else:
            self.saveflags[1]['ach']='0'
        
        if 'log' in outputslist:
            self.saveflags[2]['log']='1'
        else:
            self.saveflags[2]['log']='0'

        if 'ebw' in outputslist:
            self.saveflags[1]['exp']='1'
        else:
            self.saveflags[1]['exp']='0'


        self.saveflags[2]['srf']='0'
        self.saveflags[2]['csm']='0'
        
        #fora Jan01 Feb01, ... Nov30, Dec31
    
    
    
        
    def write(self,g):

        #print("Len aveflags",len(self.saveflags))
        #print(self.saveflags)

        for line in self.otherlines:
        
            if ('sim_af' in line):
                g.write(line)
                [ g.write(str(x)+' ') for x in self.airFlowsParameters]
                g.write('\n')
                continue

            if ('sim_mf' in line):
                g.write(line)
                [ g.write(str(x)+' ') for x in self.massFractionParameters]
                g.write('\n')
                continue

            
            if ('weather file' in line):
                g.write(self.weatherfile+' ! '+self.wcomment)
                continue
                
            if ('contaminant file' in line):
                g.write(self.contaminantfile+' ! '+self.contaminantcomment)
                continue
            
            
            if ('!date_st' in line):
                g.write(line)
                [ g.write(x+' ') for x in self.times.values() ]
                g.write('\n')
                continue
            
            if ('doDlg' in line):

                g.write(line)
                g.write(' ')
                [ g.write(x+' ') for x in self.saveflags[0].values() ]
                g.write('\n')
                continue
            
            if ('!vol' in line):

                g.write(line)
                g.write(' ')
                [ g.write(x+' ') for x in self.saveflags[1].values() ]
                g.write('\n')
                continue

            if ('!rzf' in line):

                g.write(line)
                g.write(' ')
                [ g.write(x+' ') for x in self.saveflags[2].values() ]
                g.write('\n')
                continue
            
            
            g.write(line)
        
        return
        

def convert_cols(df):

    for col in df.columns:
    
   
        df[col]=pd.to_numeric(df[col],downcast='integer',errors='ignore') #convert to numerci what can be converted
        #pd.to_numeric(x[0],downcast='integer')    
        #if (df[col].astype(int,errors='ignore')==df[col]).all():
    
        #    df[col]=df[col].astype('int',errors='ignore') # convert strings in int if possible so that all indexes are int

        #if (col=='values'):
        df[col]=df[col].astype(object)                # convert back to "object" type in order to facilite manipulations with pandas

    return df


def convertTimeString(tstring):

    if('min' in tstring):
    
        nminutes=tstring.replace('min','')
        if (int(nminutes)<60):
            return '00:'+nminutes.zfill(2)+':00'

        else:
            nhours=str(int(nminutes/60))
            nminutes=str(nminutes%60)

            return nhours.zfill(2)+':'+nminutes.zfill(2)+':00'

        
    if ('H' in tstring or 'h' in tstring):

        nhours=tstring.replace('H','').replace('h','')
    
        return nhours.zfill(2)+':00:00'





