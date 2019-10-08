# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 16:03:31 2019

@author: charles.tan
"""

sheetId = '1rlc8Wltr15SCLie4QrbiZjNQXSkD7l19dbBixdhTuCg'

data_range = 'Results'
lookup_range = 'ScrutineerLookup'
results_range = 'Results2'
#sheetId = '1SohobNnQDLN1T95Wl3jMD0QEgV7VgPlX-3pZH43rcE4'
#data_range ='results-20190913-110925'
#results_range ='test'

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
df = df.sort_values(['Question', 'Attribute', 'Cut', 'Answer'])
df.loc[:, 'Abs_Lift'] = df.loc[:,'Conv_Exp'] - df.loc[:, 'Conv_Con']
df.loc[:, '%'] = '%'

def make_percent(series, decimals):
    percent = series*100
    percent.round(decimals)
    str_percent = percent.round(decimals).astype(dtype='str')
    return(str_percent.str.cat(df['%'], sep=''))

df.loc[:, 'Summary'] = df.loc[:, 'Significance'].str.cat(make_percent(df.loc[:, 'Abs_Lift'], 2), sep=': ')
df.loc[:, 'Summary'] = df.loc[:, 'Summary'].str.cat(make_percent(df.loc[:, 'Conv_Con'], 2), sep='\n')
df.loc[:, 'Summary'] = df.loc[:, 'Summary'].str.cat(make_percent(df.loc[:, 'Conv_Exp'], 2), sep=' - ')

# create lookup table
lookup_df = df.copy()
lookup_df['identifier'] = df['Attribute'].str.cat(df['Cut'], sep='|')
lookup_df['identifier'] = lookup_df['identifier'].str.cat(df['QuestionTitle'], sep='|')
lookup_df['identifier'] = lookup_df['identifier'].str.cat(df['Answer'], sep='|')
lookup_df['identifier'] = lookup_df['identifier'].str.cat(df['AnswerValue'], sep=': ')

lookup_df = lookup_df[['identifier', 'Significance', 'Summary']]
lookup_values = []
lookup_values.append(lookup_df.columns.to_list())
for row in lookup_df.values.tolist():
    lookup_values.append(row)
    
sheetManager.update_values(sheetId=sheetId,
                           update_range=lookup_range,
                           values=lookup_values)

# create "header" area
questions = df.groupby(['Question', 'QuestionTitle', 'Answer'])['AnswerValue'].last()

questions = questions.reset_index()

values = []
buffer_size = 2 # so there is room for the attribute and cuts columns
questions_row = []
answers_row = []
#code_no_lift_row =['Codes:', 'Code No Lift']
#code_lift_row = ['Significance: 2\nAbs Lift: 3', 'Code Lift']
metric_row = []
for x in range(buffer_size):
    questions_row.append('')
    answers_row.append('')
    metric_row.append('')

for question in questions['QuestionTitle'].unique():
    metric = df.loc[df['QuestionTitle'] == question, 'QuestionCategory'].unique()[0]
    gaps = len(questions.loc[questions['QuestionTitle'] == question, 'Answer'].unique())-1
    questions_row.append(question)
    for gap in range(gaps):
#        questions_row.append('')
        questions_row.append(question)
    answers = questions.loc[questions['QuestionTitle'] == question, 'Answer'].str.cat(questions.loc[questions['QuestionTitle'] == question, 'AnswerValue'], sep=': ')
    for answer in answers:
        answers_row.append(answer)
#        code_no_lift_row.append(2)
#        code_lift_row.append(2)
        metric_row.append(metric)

values.append(questions_row)
values.append(answers_row)
#values.append(code_no_lift_row)
#values.append(code_lift_row)
values.append(metric_row)

# leave one row for the array formula
len_of_header = len(answers_row)
len_of_array_formula_row = len_of_header - buffer_size
array_formula_row = []
for x in range(buffer_size):
    array_formula_row.append('')
for cell in range(len_of_array_formula_row):
    array_formula_row.append('=concatenate("Placeholder for array formula. Attribute is: ", ADDRESS(ROW(),1, 3))')
    
#values.append(array_formula_row)
    
lookup_col = 3
formula = '=vlookup(concatenate(index(indirect(address(row(), 1, 3, TRUE))),"|",index(indirect(address(row(), 2, 3, TRUE))),"|",index(indirect(address(1,column(),2,TRUE))),"|",index(indirect(address(2,column(),2,TRUE)))), ScrutineerLookup!A:Z, '+str(lookup_col)+', false)'

# create the attribute and cut columns
cuts = df.groupby(['Attribute', 'Cut'])['Significance'].last().reset_index()
for row in cuts[['Attribute', 'Cut']].values.tolist():
    pair = []
    for item in row:
        pair.append(item)
    for x in range(len_of_array_formula_row):
        pair.append(formula)
    values.append(pair)


sheetManager.update_values(sheetId=sheetId,
                           update_range=results_range,
                           values=values)