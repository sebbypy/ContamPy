import os


filesToDelete = ['simpleModel.ach',
                 'simpleModel.log',
                 'simpleModel.prj',
                 'simpleModel.rst',
                 'simpleModel.sim',
                 'simpleModel.xlog',
                 'simpleModel.console']


for file in filesToDelete:
   
    if os.path.exists(file):  
        
        try:
            os.remove(file)
            print(file+" deleted")
        except:
            print("Error deleting "+file)
            print("Maybe it is opened ? ")
            
            
            
