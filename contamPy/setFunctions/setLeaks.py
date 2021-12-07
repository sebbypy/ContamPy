
import contam_functions


def apply(contam_data):

        
    zones=contam_data['zones']
    flowpaths=contam_data['flowpaths']
    flowelems=contam_data['flowelems']


    if (flowelems.df['name'].isin(['IL']).max() == False):
        flowelems.addflowelem('IL',{})

    defaultelemID=flowelems.df[flowelems.df['name']=='DefaultPath'].index[0]         

    leakElementID=flowelems.df[flowelems.df['name']=='IL'].index[0]         


    for roomid1 in zones.df.index:

        for roomid2 in zones.df.index:
            
            commonflowpaths=contam_functions.getcommonpaths(flowpaths,roomid1,roomid2)    
            

            for flowPathID in commonflowpaths.index:
                
                if commonflowpaths.loc[flowPathID,'pe'] == leakElementID:
                    #avoid defining a second leak when the combination romm1/room2 is reversed
                    break
                
                
                if commonflowpaths.loc[flowPathID,'pe'] == defaultelemID:
            
                    
                    flowpaths.df.loc[flowPathID,'pe']=leakElementID
                    flowpaths.df.loc[flowPathID,'mult']=float(1.0)
                    break
        











