import os


filesToDelete = ['MHRV-RIJ2-BALANCED-FILTERS.ach',
                 'MHRV-RIJ2-BALANCED-FILTERS.log',
                 'MHRV-RIJ2-BALANCED-FILTERS.prj',
                 'MHRV-RIJ2-BALANCED-FILTERS.rst',
                 'MHRV-RIJ2-BALANCED-FILTERS.sim',
                 'MHRV-RIJ2-BALANCED-FILTERS.xlog',
                 'MHRV-RIJ2-BALANCED-FILTERS.console',
                 'concentrationsPM25.pdf',
                 'concentrationsPM10.pdf'
                 ]


for file in filesToDelete:
   
    if os.path.exists(file):  
        
        try:
            os.remove(file)
            print(file+" deleted")
        except:
            print("Error deleting "+file)
            print("Maybe it is opened ? ")
            
            
            
