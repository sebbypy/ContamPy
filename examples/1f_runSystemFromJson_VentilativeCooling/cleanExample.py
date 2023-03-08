import os


filesToDelete = ['MHRV-And-VentilativeCooling.ach',
                 'MHRV-And-VentilativeCooling.log',
                 'MHRV-And-VentilativeCooling.prj',
                 'MHRV-And-VentilativeCooling.rst',
                 'MHRV-And-VentilativeCooling.sim',
                 'MHRV-And-VentilativeCooling.xlog',
                 'MHRV-And-VentilativeCooling.console']


for file in filesToDelete:
   
    if os.path.exists(file):  
        
        try:
            os.remove(file)
            print(file+" deleted")
        except:
            print("Error deleting "+file)
            print("Maybe it is opened ? ")
            
            
            
