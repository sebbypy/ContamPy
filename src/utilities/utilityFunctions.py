# -*- coding: utf-8 -*-
"""
Created on Mon Oct  3 15:37:44 2022

@author: spec
"""


def shortenTooLongName(varName,maxNumberOfChars):
    """shorten string that are too long for contam. 
    if last char is a digit, I keep it, then shorten the string and re-add the number"""
    
    name = varName    

    if len(varName) > maxNumberOfChars:

        lastChar = name[-1]
        
        if lastChar.isdigit():
            name = name[:maxNumberOfChars-1]
            name += lastChar                

        else:
            name=name[:maxNumberOfChars]
        
        
    return name

