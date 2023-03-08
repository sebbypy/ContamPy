
def apply(contam_data,numericalParameters):

    siminputs=contam_data['siminputs']
    siminputs.setdefaultstimes() # 5min time step, jan01 to dec31, 24:00 log, output 5m
    
    siminputs.settimestep(numericalParameters['simulationTimeStep'])   
    siminputs.setstartend(numericalParameters['StartDate'],numericalParameters['EndDate'])
    siminputs.setoutputfreq(numericalParameters['outputTimeStep'])
    siminputs.setoutputs(numericalParameters['outputFiles']) 
    
    
    
    



