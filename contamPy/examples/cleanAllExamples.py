import os 
import sys
import subprocess

#using subprocesses to make sure all tests are independent

import runAllExamples

def clean(tests):

    for folder,script in tests:
    
        print("Cleaning ",folder)
    
        e,o = subprocess.getstatusoutput('cd '+folder+';python3 cleanExample.py; cd ..')



if __name__=='__main__':

    clean(runAllExamples.tests)

    

