import os



filesToDelete = ['houseWithSlopedRoofNoDim-areas-empty.csv',
                 'houseWithSlopedRoofWithDimensions.prj'
                 ]

for file in filesToDelete:
    
    if os.path.exists(file):  
        
        try:
            os.remove(file)
            print(file+" deleted")
        except:
            print("Error deleting "+file)
            print("Maybe it is opened ? ")
            
            
            
