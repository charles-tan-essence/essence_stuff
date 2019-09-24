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
#df.to_csv('raw.csv', encoding='utf_8_sig', index=False)
print(df.columns)

df.loc[:, 'Significance'] = 'No Lift'
df.loc[df['Min_Abs_Lift_80'] > 0, 'Significance'] = 'Directional Lift'
df.loc[df['Min_Abs_Lift_90'] > 0, 'Significance'] = 'Significant Lift'
df.loc[df['Min_Abs_Lift_95'] > 0, 'Significance'] = 'Strong Significant Lift'
df.loc[:, 'Abs_Lift'] = df.loc[:,'Conv_Exp'] - df.loc[:, 'Conv_Con']

#df = df[['Attribute', 'Cut', 'Question', 'QuestionCategory', 'Answer', 'Conv_Con', 'Conv_Exp', 'Abs_Lift', 'Significance']]
#df = df.sort_values(by=['Question', 'Attribute', 'Cut', 'Answer'])
df = df[['Attribute', 'Cut', 'Question', 'QuestionTitle', 'QuestionCategory', 'Answer', 'AnswerValue', 'Conv_Con', 'Conv_Exp', 'Abs_Lift', 'Significance']]
df = df.sort_values(by=['Question', 'Attribute', 'Cut', 'Answer'])

#df = df.set_index(['Attribute', 'Cut'])

#print(df)
df.to_csv('results.csv', encoding='utf_8_sig', index=False)

# let's try to make it pretty with multi level indexing

# =============================================================================
# cols = [] 
# cols.append(df['Question'].to_list())
# cols.append(df['Answer'].to_list())
# 
# #cols = list(zip(*cols))
# #cols = pd.MultiIndex.from_tuples(cols, names = ['Question', 'Answer'])
# 
# #cols = pd.MultiIndex.from_arrays(arrays = cols, names = ['Question', 'Answer'])
# cols = pd.MultiIndex.from_frame(df[['Question', 'Answer']])
# 
# s = pd.Series(np.random.randn(len(df['Question'].to_list())), index=cols)
# print(s)
# 
# index = []
# index.append(df['Attribute'].to_list())
# index.append(df['Cut'].to_list())
# index = pd.MultiIndex.from_arrays(arrays = index, names = ['Attribute', 'Cut'])
# =============================================================================

