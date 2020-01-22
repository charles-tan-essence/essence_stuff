# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 15:57:14 2020

@author: charles.tan
"""

import numpy as np
import pandas as pd
from googleapiclient.discovery import build

#from authentication.authenticator import Authenticator
#from sheets.sheetmanager import SheetManager

keys = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive']

#authenticator = Authenticator(keys)
#creds = authenticator.get_creds(SCOPES)
#manager = SheetManager(creds)

spreadsheetId = '1-Rr5HJ3yonZsUTLLVzBuHKdNCarIB1BgexqpfHRU9ak'
data_range = 'Calculator'




#data = manager.get_values(spreadsheetId=spreadsheetId,
#                          data_range=data_range)

def total_sample(total_sample, control, exposed):
    if control and exposed:
        total_sample = control + exposed
        return total_sample

#data = data.apply(lambda x: total_sample( x['total sample'],
#                                  x['control'],
#                                  x['exposed']),
#    axis=1)
    
print(data)