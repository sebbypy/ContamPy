import os


filesToDelete = ['VentilativeCooling.ach',
                 'VentilativeCooling.log',
                 'VentilativeCooling.prj',
                 'VentilativeCooling.rst',
                 'VentilativeCooling.sim',
                 'VentilativeCooling.xlog',
                 'VentilativeCooling.console']


for file in filesToDelete:
   
    if os.path.exists(file):  
        
        try:
            os.remove(file)
            print(file+" deleted")
        except:
            print("Error deleting "+file)
            print("Maybe it is opened ? ")
            
            
            
