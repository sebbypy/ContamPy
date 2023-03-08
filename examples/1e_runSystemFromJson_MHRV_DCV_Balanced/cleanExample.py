import os


filesToDelete = ['MHRV-RIJ2-DCV-BALANCED.ach',
                 'MHRV-RIJ2-DCV-BALANCED.log',
                 'MHRV-RIJ2-DCV-BALANCED.prj',
                 'MHRV-RIJ2-DCV-BALANCED.rst',
                 'MHRV-RIJ2-DCV-BALANCED.sim',
                 'MHRV-RIJ2-DCV-BALANCED.xlog',
                 'MHRV-RIJ2-DCV-BALANCED.console',
                 'supplyFlows.pdf',
                 'extractFlows.pdf',
                 'flowBalance.pdf']


for file in filesToDelete:
   
    if os.path.exists(file):  
        
        try:
            os.remove(file)
            print(file+" deleted")
        except:
            print("Error deleting "+file)
            print("Maybe it is opened ? ")
            
            
            
