
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

    print(zones.df)

    #-------------------------------------------------------------
    # Editing CONTAM model as a function of the system description
    #-------------------------------------------------------------

    # Mechanical exhaust
    # -------------------
    for ME in systemJson['Mechanical exhaust']:
        
        ahsreturn=ahs.df.loc[1,'zr#']
        zoneid=zones.df[zones.df['name']==ME['Room']].index[0] # find ID of zone which has the same name

        print("ezone id",zoneid)
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
            
            print(W['Room'])
            print(zones.df)
            
            zoneid=zones.df[zones.df['name']==W['Room']].index[0] # find ID of zone which has the same name
            
            #flowpath index
            fpid=flowpaths.df[ (flowpaths.df['pzm']==zoneid) & (flowpaths.df['pe']==generic_NSV_id) ].index
           
            print("Defining Window opening for room"+W['Room'])
            
            if (len(fpid)==0):
                print("WARINING: No natural supply could be defined !")
                print("No existing path between ",zones.df.loc[zoneid,'name'],"and outside")
                continue
                
            if (len(fpid)>1):
                print("WARNING, more than one location to define natural supply")
                print("Choosing the first one in the list, please check your model afterwards")
                fpid = fpid[0]

            W_name='Window-Cd01'

            flowpaths.df.loc[fpid,'pe']=flowelems.df[flowelems.df['name']==W_name].index[0]
            flowpaths.df.loc[fpid,'mult']=float(W['Area'])



    for NT in systemJson['Natural transfer']:
        
        #print("")

        #print(zones.df)
        #print(NT)
        #input("...")

        generic_NT_id = flowelems.df[flowelems.df['name']=='Gen_NT'].index[0]

        roomid1=zones.df[zones.df['name']==NT['From room']].index[0] # find ID of zone which has the same name
        roomid2=zones.df[zones.df['name']==NT['To room']].index[0] # find ID of zone which has the same name
        commonflowpaths=contam_functions.getcommonpaths(flowpaths,roomid1,roomid2)    

        #print("")
        #print("Defining Natural Transfer from "+NT['From room']+' to '+NT['To room']+'('+str(NT['Capacity'])+' m3/h at '+str(NT['Design pressure'])+' Pa)')
      

        if (len(commonflowpaths[commonflowpaths['pe']==generic_NT_id].index)==1):
            fpid=commonflowpaths[commonflowpaths['pe']==generic_NT_id].index[0]
        else:
            print("Error")
            print("No path detected between "+NT['From room']+' and '+NT['To room']+' to define a transfer opening')
            return

        #check if flow element with the required pressure exist
        NT_name='NT_'+str(NT['Design pressure'])+'Pa'

        if (flowelems.df['name'].isin([NT_name]).max() == False):
            print(NT_name+' element does not exist yet, adding it')
            flowelems.addflowelem('NT',{'dp':int(NT['Design pressure'])})

        flowpaths.df.loc[fpid,'pe']=flowelems.df[flowelems.df['name']==NT_name].index[0]
        flowpaths.df.loc[fpid,'mult']=float(NT['Capacity'])
        

        flowpaths.df.loc[fpid,'pe']

