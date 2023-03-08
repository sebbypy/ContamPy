import os


filesToDelete = ['houseWithSlopedRoofWithDimensions-blowerDoor.val',
                 'houseWithSlopedRoofWithDimensions-blowerDoor.log',
                 'houseWithSlopedRoofWithDimensions-blowerDoor.prj',
                 'houseWithSlopedRoofWithDimensions-blowerDoor.rst',
                 'houseWithSlopedRoofWithDimensions-blowerDoor.sim',
                 'houseWithSlopedRoofWithDimensions-blowerDoor.xlog',
                 'houseWithSlopedRoofWithDimensions-blowerDoor.console']


for file in filesToDelete:
   
    if os.path.exists(file):  
        
        try:
            os.remove(file)
            print(file+" deleted")
        except:
            print("Error deleting "+file)
            print("Maybe it is opened ? ")
            
            
            
