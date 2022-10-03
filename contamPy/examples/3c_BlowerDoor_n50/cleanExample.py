import os


filesToDelete = ['BlowerDoor.val',
                 'BlowerDoor.log',
                 'BlowerDoor.prj',
                 'BlowerDoor.rst',
                 'BlowerDoor.sim',
                 'BlowerDoor.xlog',
                 'BlowerDoor.console']


for file in filesToDelete:
   
    if os.path.exists(file):  
        
        try:
            os.remove(file)
            print(file+" deleted")
        except:
            print("Error deleting "+file)
            print("Maybe it is opened ? ")
            
            
            
