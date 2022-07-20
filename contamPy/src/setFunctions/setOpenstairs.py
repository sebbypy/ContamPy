
import contam_functions


def apply(contam_data):

        
    zones=contam_data['zones']
    flowpaths=contam_data['flowpaths']
    flowelems=contam_data['flowelems']


    large_opening_id=flowelems.df[flowelems.df['name']=='LargeOpening'].index[0]


    for roomid1 in zones.df.index:

        for roomid2 in zones.df.index:
            
            commonflowpaths=contam_functions.getcommonpaths(flowpaths,roomid1,roomid2)    

            verticalflowpaths = commonflowpaths[commonflowpaths['dir'].isin([3,6])]            

            for flowPathID in verticalflowpaths.index:
                
                if commonflowpaths.loc[flowPathID,'pe'] == large_opening_id:
                    flowpaths.df.loc[flowPathID,'mult']=float(1.0)
                    break
        











