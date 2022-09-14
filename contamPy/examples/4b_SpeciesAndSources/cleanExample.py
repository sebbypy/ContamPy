import os


filesToDelete = ['MHRV-RIJ2-BALANCED.ach',
                 'MHRV-RIJ2-BALANCED.log',
                 'MHRV-RIJ2-BALANCED.prj',
                 'MHRV-RIJ2-BALANCED.rst',
                 'MHRV-RIJ2-BALANCED.sim',
                 'MHRV-RIJ2-BALANCED.xlog',
                 'MHRV-RIJ2-BALANCED.console',
                 'PM2.5.pdf',
                 'CO2.pdf',
                 'FIC.pdf',
                 'HCHO.pdf'
                 ]


for file in filesToDelete:
   
    if os.path.exists(file):  
        
        try:
            os.remove(file)
            print(file+" deleted")
        except:
            print("Error deleting "+file)
            print("Maybe it is opened ? ")
            
            
            
