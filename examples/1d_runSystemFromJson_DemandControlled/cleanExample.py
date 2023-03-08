import os


filesToDelete = ['MEV-RIJ2.ach',
                 'MEV-RIJ2.log',
                 'MEV-RIJ2.prj',
                 'MEV-RIJ2.rst',
                 'MEV-RIJ2.sim',
                 'MEV-RIJ2.xlog',
                 'MEV-RIJ2.console']


for file in filesToDelete:
   
    if os.path.exists(file):  
        
        try:
            os.remove(file)
            print(file+" deleted")
        except:
            print("Error deleting "+file)
            print("Maybe it is opened ? ")
            
            
            
