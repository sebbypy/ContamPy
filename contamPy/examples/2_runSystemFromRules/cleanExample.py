import os


filesToDelete = ['MEV-RIJ2-namedSystem.ach',
                 'MEV-RIJ2-namedSystem.log',
                 'MEV-RIJ2-namedSystem.prj',
                 'MEV-RIJ2-namedSystem.rst',
                 'MEV-RIJ2-namedSystem.sim',
                 'MEV-RIJ2-namedSystem.xlog',
                 'MEV-RIJ2-namedSystem.console',
                 'MEV-RIJ2-namedSystem.json']


for file in filesToDelete:
   
    if os.path.exists(file):  
        
        try:
            os.remove(file)
            print(file+" deleted")
        except:
            print("Error deleting "+file)
            print("Maybe it is opened ? ")
            
            
            
