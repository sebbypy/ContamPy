

def setFilters(contam_data,fullJSON):

    # ----------------------------------
    # Load CONTAM FILE and various parts
    # ----------------------------------

    zones=contam_data['zones']
    ahs=contam_data['ahs']

    flowpaths=contam_data['flowpaths']
    filterElements = contam_data['filterelements']
    filters = contam_data['filters']
    

    #expected paramsDict {'name':'shortName','description':'long description',efficiencies{'specie1':'Efficiency1','specie2':efficiency2}


    for filterElem in fullJSON['Filters']:
        
        filterElements.add(filterElem)


    for MS in fullJSON['Mechanical supply']:
        
        if "Filter" in MS.keys():
            
            filterName = MS["Filter"]

            
            filterID = filters.add(filterName,filterElements) #adding in list of actual filters in CTM
            
            ahssupply = ahs.df.loc[1,'zs#']
            zoneid = zones.df[ zones.df['name'] == MS['Room'] ].index[0] # find ID of zone which has the same name
            fpid=flowpaths.df[ (flowpaths.df['pzm']==zoneid) & (flowpaths.df['pzn'] == ahssupply) ].index[0]

            flowpaths.df.loc[fpid,'pf'] = filterID
            

            

