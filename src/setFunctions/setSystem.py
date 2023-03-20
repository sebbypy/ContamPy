
import contam_functions


def apply(contam_data,systemJson):

    # ----------------------------------
    # Load CONTAM FILE and various parts
    # ----------------------------------

    zones=contam_data['zones']
    flowpaths=contam_data['flowpaths']
    flowelems=contam_data['flowelems']
    ahs=contam_data['ahs']

    # ----------------
    # Load SYSTEM file
    # ----------------


    #-------------------------------------------------------------
    # Editing CONTAM model as a function of the system description
    #-------------------------------------------------------------

    # Mechanical exhaust
    # -------------------
    for ME in systemJson['Mechanical exhaust']:
        
        ahsreturn=ahs.df.loc[1,'zr#']
        zoneid=zones.df[zones.df['name']==ME['Room']].index[0] # find ID of zone which has the same name

        #flowpath index
        fpid=flowpaths.df[ (flowpaths.df['pzn']==zoneid) & (flowpaths.df['pzm'] == ahsreturn) ].index[0]
        
        flowpaths.df.loc[fpid,'Fahs']=float(ME['Nominal flow rate'])/3600*1.2041

    # Mechanical supply
    # -----------------

    for MS in systemJson['Mechanical supply']:
        
        ahssupply=ahs.df.loc[1,'zs#']
        zoneid=zones.df[zones.df['name']==MS['Room']].index[0] # find ID of zone which has the same name
        
        #flowpath index
        fpid=flowpaths.df[ (flowpaths.df['pzm']==zoneid) & (flowpaths.df['pzn'] == ahssupply) ].index[0]

        flowpaths.df.loc[fpid,'Fahs']=float(MS['Nominal flow rate'])/3600*1.2041

    # Natural supply
    # --------------

    for NS in systemJson['Natural supply']:
        
        generic_NSV_id = flowelems.df[flowelems.df['name']=='Gen_NSV'].index[0]  
        zoneid=zones.df[zones.df['name']==NS['Room']].index[0] # find ID of zone which has the same name
        
        #flowpath index
        fpid=flowpaths.df[ (flowpaths.df['pzm']==zoneid) & (flowpaths.df['pe']==generic_NSV_id) ].index

        
        #print("")
        #print("Defining Natural Supply for "+NS['Room']+' ('+str(NS['Capacity'])+' m3/h at '+str(NS['Design pressure'])+' Pa - Self-regulating: '+NS['Self-Regulating']+')')
        
        if (len(fpid)==0):
            print("WARINING: No natural supply could be defined !")
            print("No existing path between ",zones.df.loc[zoneid,'name'],"and outside")
            continue
            
        if (len(fpid)>1):

            if 'Preferred orientation' in NS.keys():
                print("Chosing preferend orientation")
                fpid=flowpaths.df[ (flowpaths.df['pzm']==zoneid) & (flowpaths.df['pe']==generic_NSV_id) & (flowpaths.df['wazm']== int(NS['Preferred orientation'])) ].index
                
                if len(fpid)==0: 
                    print("WARNING: No windows could be defined !")
                    print("No existing path between ",zones.df.loc[zoneid,'name'],"and outside on the facade",NS['Preferred orientation'],"°")
                    continue

            else:
                print("WARNING, more than one location to define natural supply")
                print("Choosing the first one in the list, please check your model afterwards")
                fpid = fpid[0]

                    


        #check if flow element with the required pressure exist
        if (NS['Self-Regulating']=='No'):
            NSV_name='NSV_'+str(NS['Design pressure'])+'Pa'
        else:
            NSV_name='SR_NSV_'+str(NS['Design pressure'])+'Pa'

        if (flowelems.df['name'].isin([NSV_name]).max() == False):
            #print(NSV_name+' element does not exist yet, adding it')

            if (NS['Self-Regulating']=='No'):
                flowelems.addflowelem('NSV',{'dp':int(NS['Design pressure'])})
            else:
                flowelems.addflowelem('SR_NSV',{'dp':int(NS['Design pressure'])})


        flowpaths.df.loc[fpid,'pe']=flowelems.df[flowelems.df['name']==NSV_name].index[0]
        flowpaths.df.loc[fpid,'mult']=float(NS['Capacity'])
        
        #print("Ok")

    if ('Windows' in systemJson.keys()):

        for W in systemJson['Windows']:
            
            #one assumes that there will be no (active) windows in the same room as a NSV ! 
            # QUID FOR HYBRID VENTILATION ?? (low probability of window + natural supply...)
            
            generic_NSV_id = flowelems.df[flowelems.df['name']=='Gen_NSV'].index[0]  
            
            
            zoneid=zones.df[zones.df['name']==W['Room']].index[0] # find ID of zone which has the same name
            
            #flowpath index
            fpid=flowpaths.df[ (flowpaths.df['pzm']==zoneid) & (flowpaths.df['pe']==generic_NSV_id) ].index
           
            
            if (len(fpid)==0):
                print("WARINING: No natural supply could be defined !")
                print("No existing path between ",zones.df.loc[zoneid,'name'],"and outside")
                continue
                
            if (len(fpid)>1):
                 
                 if W['Preferred orientation'] =="":
                    
                    fpid = fpid[0]
                    
                    print("WARNING, more than one location to define windows")
                    print("Choosing the first one in the list, please check your model afterwards")
                 else:
                    
                    fpid=flowpaths.df[ (flowpaths.df['pzm']==zoneid) & (flowpaths.df['pe']==generic_NSV_id) & (flowpaths.df['wazm']== int(W['Preferred orientation'])) ].index
                    
                    if len(fpid)==0: 
                        print("WARNING: No windows could be defined !")
                        print("No existing path between ",zones.df.loc[zoneid,'name'],"and outside on the facade",W['Preferred orientation'],"°")
                        continue
                
            
            if W['Type']=='normalwindow':
                
                W_name = 'NW'+'_'+str(float(W['Height']))+'_'+str(float(W['Width']))
                if (flowelems.df['name'].isin([W_name]).max() == False):
                    flowelems.addflowelem('NW',{'h':float(W['Height']),'w':float(W['Width']) })
                
              
            if W['Type']=='roofwindow':
                W_name = 'RW'+'_'+str(float(W['Height']))+'_'+str(float(W['Width']))
                #print(W_name)
                if (flowelems.df['name'].isin([W_name]).max() == False):
                    flowelems.addflowelem('RW',{'h':float(W['Height']),'w':float(W['Width']) })
                
            flowpaths.df.loc[fpid,'pe']=flowelems.df[flowelems.df['name']==W_name].index[0]
            flowpaths.df.loc[fpid,'mult']=float(1.0)



    for NT in systemJson['Natural transfer']:
        

        generic_NT_id = flowelems.df[flowelems.df['name']=='Gen_NT'].index[0]

        roomid1=zones.df[zones.df['name']==NT['From room']].index[0] # find ID of zone which has the same name
        roomid2=zones.df[zones.df['name']==NT['To room']].index[0] # find ID of zone which has the same name
        commonflowpaths=contam_functions.getcommonpaths(flowpaths,roomid1,roomid2)    

      

        if (len(commonflowpaths[commonflowpaths['pe']==generic_NT_id].index)==1):
            fpid=commonflowpaths[commonflowpaths['pe']==generic_NT_id].index[0]
        else:
            print("Error")
            print("No path detected between "+NT['From room']+' and '+NT['To room']+' to define a transfer opening')
            return

        #check if flow element with the required pressure exist
        NT_name='NT_'+str(NT['Design pressure'])+'Pa'

        if (flowelems.df['name'].isin([NT_name]).max() == False):
            flowelems.addflowelem('NT',{'dp':int(NT['Design pressure'])})

        flowpaths.df.loc[fpid,'pe']=flowelems.df[flowelems.df['name']==NT_name].index[0]
        flowpaths.df.loc[fpid,'mult']=float(NT['Capacity'])
        

        flowpaths.df.loc[fpid,'pe']



    # comes after NT: if already NT existing, the NT is replaced by OD
    if ('Open doors' in systemJson.keys()):
        for OD in systemJson['Open doors']:
            roomid1=zones.df[zones.df['name']==OD['From room']].index[0] # find ID of zone which has the same name
            roomid2=zones.df[zones.df['name']==OD['To room']].index[0] # find ID of zone which has the same name
            commonflowpaths=contam_functions.getcommonpaths(flowpaths,roomid1,roomid2)    
         
    
            if (len(commonflowpaths) > 0):
                fpid=commonflowpaths.index[0] #NT is index 0 if exists - anyway, I use index 0 
            else:
                print("Error")
                print("No path detected between "+OD['From room']+' and '+OD['To room']+' to define a transfer opening')
                return
    
            if (flowelems.df['name'].isin(['OD']).max() == False):
                flowelems.addflowelem('OD',{})
    
            flowpaths.df.loc[fpid,'pe']=flowelems.df[flowelems.df['name']=='OD'].index[0]
            flowpaths.df.loc[fpid,'mult']=float(1.0)
        

    if ('Two ways door' in systemJson.keys()):
         
         for D in systemJson['Two ways door']:
            roomid1=zones.df[zones.df['name']==D['From room']].index[0] # find ID of zone which has the same name
            roomid2=zones.df[zones.df['name']==D['To room']].index[0] # find ID of zone which has the same name
            commonflowpaths=contam_functions.getcommonpaths(flowpaths,roomid1,roomid2)  
            if (len(commonflowpaths) > 0):
                fpid=commonflowpaths.index[0] #un des defaults paths
                
            else:
                print("Error")
                print("No path detected between "+D['From room']+' and '+D['To room']+' to define a transfer opening')
                return
            
           
            D_name='D'+'_'+str(float(D['Height']))+'_'+str(float(D['Width']))
            if (flowelems.df['name'].isin([D_name]).max() == False):
                flowelems.addflowelem('D',{'h':int(D['Height']),'w':int(D['Width']) })
            
            flowpaths.df.loc[fpid,'pe']=flowelems.df[flowelems.df['name']==D_name].index[0]
            flowpaths.df.loc[fpid,'mult']=float(1.0)
         
            
         
         # Ventilative cooling component
         # --------------
    if ('Ventilative cooling component' in systemJson.keys()):
    
    
        for VC in systemJson['Ventilative cooling component']:
            
            print("### PASS ###")
            
            generic_VCC_id = flowelems.df[flowelems.df['name']=='Gen_OP'].index[0]  
            zoneid=zones.df[zones.df['name']==VC['Room']].index[0] # find ID of zone which has the same name
            #print(flowpaths.df[flowpaths.df['pe']==generic_VCC_id])
            #flowpath index
            fpid=flowpaths.df[ (flowpaths.df['pzm']==zoneid) & (flowpaths.df['pe']==generic_VCC_id) ].index
            
        
            if (len(fpid)==0):
                print("WARINING: No ventilative cooling could be defined !")
                print("No existing path between ",zones.df.loc[zoneid,'name'],"and outside")
                continue
            
            if (len(fpid)>1):
               
                
                if VC['Preferred orientation'] =="":
                    
                    fpid = fpid[0]
                    
                    print("WARNING, more than one location to define ventilative cooling")
                    print("Choosing the first one in the list, please check your model afterwards")
                    
                    
                else:
                    
                    fpid=flowpaths.df[ (flowpaths.df['pzm']==zoneid) & (flowpaths.df['pe']==generic_VCC_id) & (flowpaths.df['wazm']== int(VC['Preferred orientation'])) ].index
                    
                    if len(fpid)==0: 
                        print("WARNING: No ventilative cooling could be defined !")
                        print("No existing path between ",zones.df.loc[zoneid,'name'],"and outside on the facade",VC['Preferred orientation'],"°")
                        continue
                   

        #check if flow element with the required pressure exist
        
            Cd=VC['Discharge coefficient']
        
            VCC_name='VCC_'+str(Cd)

            if (flowelems.df['name'].isin([VCC_name]).max() == False):
                flowelems.addflowelem('VCC',{'Cd':Cd})
            
            flowpaths.df.loc[fpid,'pe']=flowelems.df[flowelems.df['name']==VCC_name].index[0]
            flowpaths.df.loc[fpid,'mult']=float(VC['Area'])
        






  











