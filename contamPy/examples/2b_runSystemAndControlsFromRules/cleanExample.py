import os


filesToDelete = ['MEV-RIJ2-namedSystemWithControls.ach',
                 'MEV-RIJ2-namedSystemWithControls.log',
                 'MEV-RIJ2-namedSystemWithControls.prj',
                 'MEV-RIJ2-namedSystemWithControls.rst',
                 'MEV-RIJ2-namedSystemWithControls.sim',
                 'MEV-RIJ2-namedSystemWithControls.xlog',
                 'MEV-RIJ2-namedSystemWithControls.console']


for file in filesToDelete:
   
    if os.path.exists(file):  
        
        try:
            os.remove(file)
            print(file+" deleted")
        except:
            print("Error deleting "+file)
            print("Maybe it is opened ? ")
            
            
            
