
def apply(contam_data,weatherfile):


    siminputs=contam_data['siminputs']
       
    siminputs.setweather(weatherfile)
    
    siminputs.setdefaultstimes() # 5min time step, jan01 to dec31, 24:00 log, output 5m
    siminputs.settimestep('00:05:00')
    siminputs.setstartend('Jan01','Dec31')
    siminputs.setoutputfreq('00:05:00')
    
    
    #siminputs.setoutputs(['simflow','simconc','log','ach']) #only the ones listes a
    siminputs.setoutputs(['log','ach']) #only the ones list
    
    
    
    



