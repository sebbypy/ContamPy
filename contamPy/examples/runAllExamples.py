import os 
import sys
import subprocess

#using subprocesses to make sure all tests are independent


tests = [['0_modelGeneration','runAll.py'],
        ['1_runSystemFromJson','runFromJson.py'],
        ['1b_runSystemFromJson_MoreComplex','runFromJson.py'],
        ['1c_runSystemFromJson_ClockControl','runFromJson.py'],
        ['1d_runSystemFromJson_DemandControlled','runFromJson.py']
        ]


def run(tests):

    for folder,script in tests:

        e,o = subprocess.getstatusoutput('cd '+folder+';python3 '+script+'; cd ..')
        print("FOLDER ",folder)
        print("Exit code",e)
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
    
    

