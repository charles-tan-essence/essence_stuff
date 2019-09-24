# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 16:03:31 2019

@author: charles.tan
"""

sheetId = '1rlc8Wltr15SCLie4QrbiZjNQXSkD7l19dbBixdhTuCg'
data_range = 'Results'





from authenticator import Authenticator
from sheetmanager import SheetManager
import pandas as pd

keys = 'credentials.json'
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

authenticator = Authenticator(keys)
creds = authenticator.get_creds(SCOPES)

sheetManager = SheetManager(creds)

df = sheetManager.get_values(sheetId=sheetId, data_range=data_range)
df = df[['Attribute', 'Cut', 'Question', 'Answer', 'Min_Abs_Lift_90']]

#values = ['Min_Abs_Lift_80',
#          'Min_Abs_Lift_90',
#          'Min_Abs_Lift_95']

values = ['Min_Abs_Lift_90',
          ]

def replace(value, replacement):
    if value > 0:
        return(replacement)
    else:
        return('No Lift')

#table = df.pivot_table(values = values, 
#                        index = ['Attribute', 'Cut'], 
#                        columns = ['Question', 'Answer'],
#                        aggfunc = lambda x: replace(x.item(), 'Significant Lift'))

table = df.groupby(['Attribute', 'Cut', 'Question', 'Answer']).apply(lambda x:replace(x['Min_Abs_Lift_90'].item(), 'Significant Lift'))

#print(table)

table.to_csv('results.csv', encoding='utf_8_sig')
