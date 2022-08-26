import os



filesToDelete = ['DetachedHouse_withDimensions.prj',
                'DetachedHouse_noDimensions-areas-empty.csv',
                'DetachedHouse_noDimensions-areas-filled.csv']


for file in filesToDelete:
    
    if os.path.exists(file):  
        
        try:
            os.remove(file)
            print(file+" deleted")
        except:
            print("Error deleting "+file)
            print("Maybe it is opened ? ")
            
            
            
