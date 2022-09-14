import os 
import sys
import subprocess

#using subprocesses to make sure all tests are independent


tests = [['0_modelGeneration','runAll.py'],
         ['0b_modelGenerationSlopedRoof','runAll.py'],
         ['1_runSystemFromJson','runFromJson.py'],
         ['1b_runSystemFromJson_MoreComplex','runFromJson.py'],
         ['1c_runSystemFromJson_ClockControl','runFromJson.py'],
         ['1d_runSystemFromJson_DemandControlled','runFromJson.py'],
         ['1e_runSystemFromJson_MHRV_DCV_Balanced','runFromJson.py'],
         ['2_runSystemFromRules','runFromRules.py'],
         ['2b_runSystemAndControlsFromRules','runFromRulesWithControl.py'],
         ['3_BlowerDoor','runBlowerDoor.py'],
         ['3b_BlowerDoor_fromExample_0b','runBlowerDoor.py'],
         ['4_SpeciesAndFilters','runFromJSON.py'],
         ['4b_SpeciesAndSources','runFromJSON.py']
         ]


def run(tests):

    for folder,script in tests:
        
        if os.name == 'nt':

            pythonexe = sys.executable

            e,o = subprocess.getstatusoutput('cd '+folder+'& '+pythonexe+' '+script+' & cd ..')

        if os.name == 'posix':
            
            
            e,o = subprocess.getstatusoutput('cd '+folder+';python3 '+script+'; cd ..')


        print("Example",folder)    
        print("Console output")
        print("--------------------------------------")
        print(o)
        print("--------------------------------------")

        print("")
        print("")
    
    

def clean(tests):

    for folder,script in tests:
    
        print("Cleaning ",folder)
    
        e,o = subprocess.getstatusoutput('cd '+folder+';python3 cleanExample.py; cd ..')



if __name__=='__main__':

    run(tests)
    
    

