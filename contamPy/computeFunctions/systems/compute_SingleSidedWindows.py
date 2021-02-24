
    
def compute(args):

    contam_data = args[0]
    
    #--------------------------------------------
    # Defining types (wet/dry/hal) and functions
    #--------------------------------------------
    wet=['Wasplaats','Badkamer','WC','Keuken','OKeuken']  # existing functions in dry spaces
    dry=['Slaapkamer','Woonkamer','Bureau','Speelkamer']  # existing function in wet spaces
    hal=['hal','Hal','Garage','Berging','Dressing'] #existing functions for hal

    #------------------
    # Read CONTAM model
    #------------------
    zones=contam_data['zones']

    # ----------------------------------------------
    # Assingning types and functions to model spaces
    # ----------------------------------------------
    for zoneindex in zones.df.index:
        
        zonename=zones.df.loc[zoneindex,'name']
        
        for zonetype in wet:
            if (zonetype in zonename):
            # create exhaust, natural of mechanical
                zones.df.loc[zoneindex,'type']='wet'
                zones.df.loc[zoneindex,'function']=zonetype

        for zonetype in dry:
            if (zonetype in zonename):
            # create exhaust, natural of mechanical
                zones.df.loc[zoneindex,'type']='dry'
                zones.df.loc[zoneindex,'function']=zonetype

        for zonetype in hal:
            if (zonetype in zonename):
            # create exhaust, natural of mechanical
                zones.df.loc[zoneindex,'type']='hal'
                zones.df.loc[zoneindex,'function']='hal'


    #----------------------------
    # DICTIONNARY TO WRITE DOWN
    #----------------------------
    jsondict={'Mechanical supply':[],
              'Mechanical exhaust':[],
              'Natural supply':[],
              'Natural exhaust':[],
              'Natural transfer':[],
              'Windows':[]
              }

         
    # ----------------------------
    # Defining supply and extract
    # ----------------------------
    for zoneindex in zones.df.index:
        
        if (zones.df.loc[zoneindex,'type'] in ['wet','dry']):
        
            area=float(zones.df.loc[zoneindex,'Vol'])/3.0

            Wdict={'Room':zones.df.loc[zoneindex,'name'],'Area':area/10}

            jsondict['Windows'].append(Wdict)


    
    return jsondict
