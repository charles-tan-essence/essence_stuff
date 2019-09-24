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
import numpy as np

keys = 'credentials.json'
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

authenticator = Authenticator(keys)
creds = authenticator.get_creds(SCOPES)

sheetManager = SheetManager(creds)

df = sheetManager.get_values(sheetId=sheetId, data_range=data_range)
df.to_csv('raw.csv', encoding='utf_8_sig', index=False)
print(df.columns)

df.loc[:, 'Significance'] = 'No Lift'
df.loc[df['Min_Abs_Lift_80'] > 0, 'Significance'] = 'Directional Lift'
df.loc[df['Min_Abs_Lift_90'] > 0, 'Significance'] = 'Significant Lift'
df.loc[df['Min_Abs_Lift_95'] > 0, 'Significance'] = 'Strong Significant Lift'
df.loc[:, 'Abs_Lift'] = df.loc[:,'Conv_Exp'] - df.loc[:, 'Conv_Con']

df = df[['Attribute', 'Cut', 'Question', 'QuestionCategory', 'Answer', 'Conv_Con', 'Conv_Exp', 'Abs_Lift', 'Significance']]
df = df.sort_values(by=['Question', 'Attribute', 'Cut', 'Answer'])

df = df.set_index(['Attribute', 'Cut'])

#df.columns = pd.MultiIndex.from_arrays((df['Question'], df['Answer']))

print(df)
df.to_csv('results.csv', encoding='utf_8_sig', index=True)

#values = ['Min_Abs_Lift_80',
#          'Min_Abs_Lift_90',
#          'Min_Abs_Lift_95']

#values = ['Min_Abs_Lift_90',
#          ]
#
#def replace(value, replacement):
#    if value > 0:
#        return(replacement)
#    else:
#        return('No Lift')



#table = df.pivot_table(values = values, 
#                        index = ['Attribute', 'Cut'], 
#                        columns = ['Question', 'Answer'],
#                        aggfunc = lambda x: replace(x.item(), 'Significant Lift'))

#table = df.groupby(['Attribute', 'Cut', 'Question', 'Answer']).apply(lambda x: replace(x['Min_Abs_Lift_90'].item(), 'Significant Lift'))

#table = df.groupby(['Attribute', 'Cut', 'Question', 'Answer']).mean()
#
#table = table.reset_index()
#
#table = df[['Attribute', 'Cut', 'Question', 'Answer', 'Min_Abs_Lift_90', 'Abs_Lift']]
#
#table['Significance'] = np.nan
#
#table.loc[table['Min_Abs_Lift_90'] > 0, 'Significance'] = 'Significant Lift'
#table.loc[table['Min_Abs_Lift_90'] <= 0, 'Significance'] = 'No Lift'

#print(table)

#table.to_csv('results.csv', encoding='utf_8_sig')
