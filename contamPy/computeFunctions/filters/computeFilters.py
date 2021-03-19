import sys
sys.path.append('/home/spec/Documents/Projects/RESEARCH/COMISVENT/2.Work/Python')

import copy

    
def compute(args):
    
    
    systemJson = args[0]
    
    speciesEfficiencies = args[1]
    #input arg dictionnary   {'specie1':efficiency, 'specie2':efficiency}
    
    filterJson = copy.deepcopy(systemJson)


    filterJson["Filters"]=[]
    
    filterDescription = {}
    
    filterDescription["Name"]="Filter"
    filterDescription["Description"]="This is an automatically created filter"
    filterDescription["Efficiencies"]={}

    for specie,efficiency in speciesEfficiencies.items():
        filterDescription["Efficiencies"][specie]=efficiency

    
    filterJson['Filters'].append(filterDescription)
    
    for MS in filterJson['Mechanical supply']:
        MS['Filter']='Filter'

    
    
    #json.dump(controlJson,open(controljson,'w'),indent=4)
    return filterJson

