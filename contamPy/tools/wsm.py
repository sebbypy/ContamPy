#wind speed modifier

def wsm(building_height,building_terrain_category,meteo_terrain_category):

    roughness_dict={'I':0.17,'II':0.20,'III':0.25,'IV':0.33}   # AIVC Guide to ventilation; Chapter 12
    
    Zref=building_height
    alpha_site=roughness_dict[building_terrain_category]
    
    alpha_met=roughness_dict[meteo_terrain_category]
    Zmet=10


        
    # Formulas from IWT RENSON p39

    if (alpha_site<0.34):

        Zbound=60

    else:
        Zbound=60+(alpha_site-0.34)*(10800*(alpha_site-0.34)+440)
    
    #print(Zbound)


    C=(Zref/Zbound)**(2*alpha_site)*(Zbound/Zmet)**(2*alpha_met)



    return (C)


#C=wsm(6,'II','II') --> 0.81

#print(C)
