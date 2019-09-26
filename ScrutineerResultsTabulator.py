# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 16:03:31 2019

@author: charles.tan
"""

sheetId = '1rlc8Wltr15SCLie4QrbiZjNQXSkD7l19dbBixdhTuCg'

data_range = 'Results'
results_range = 'Results2'
#sheetId = '1SohobNnQDLN1T95Wl3jMD0QEgV7VgPlX-3pZH43rcE4'
#data_range ='results-20190913-110925'
#results_range ='test'
append = None # 'vertical' or 'horizontal'

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
#df.to_csv('raw.csv', encoding='utf_8_sig', index=False)
#print(df.columns)

#df.loc[:, 'Significance'] = 'No Lift'
#df.loc[df['Min_Abs_Lift_80'] > 0, 'Significance'] = 'Directional Lift'
#df.loc[df['Min_Abs_Lift_90'] > 0, 'Significance'] = 'Significant Lift'
#df.loc[df['Min_Abs_Lift_95'] > 0, 'Significance'] = 'Strong Significant Lift'
#df.loc[df['Answer'] != 'Desired', 'Answer'] = df['Answer'].str.cat(df['AnswerValue'], sep=': ')
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

df.loc[df['Attribute'] == 'MAP QUESTION_3_0'].to_csv('results.csv', encoding='utf_8_sig')
#test = df.copy()
#test.to_csv('results.csv', encoding='utf_8_sig')

if append == 'horizontal':
    df = df.groupby(['Attribute', 'Cut', 'QuestionTitle', 'Answer'])['Summary'].last().unstack('QuestionTitle').unstack('Answer').reset_index()
    df = df.fillna('')
    df.columns.to_flat_index()
    df.to_csv('temp.csv', index=False, encoding='utf_8_sig')
#     time to do some disgusting roundabout way...
    import os
    import csv
    values = []
    with open('temp.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            values.append(row)
    os.remove('temp.csv')


if append == 'vertical':

    df = df[['Attribute', 'Cut', 'Question', 'QuestionTitle', 'QuestionCategory', 'Answer', 'AnswerValue', 'Conv_Con', 'Conv_Exp', 'Abs_Lift', 'Significance', 'Summary']]
    df = df.sort_values(by=['Question', 'Attribute', 'Cut', 'Answer'])
    
    
    df2 = df.set_index(['QuestionTitle', 'Attribute', 'Cut', 'Answer'])['Summary'].unstack().reset_index()
    
    #df2.to_csv('results.csv', encoding='utf_8_sig', index=False)
    
    df_values = df2.fillna('').values
    
    values = []
    answers_added = []
    completed_questions = []
    
    def get_max_num_of_ans_options():
        for_comparison = []
        for question in df2['QuestionTitle'].unique():
            for_comparison.append(len(df.loc[df['QuestionTitle'] == question, 'Answer'].unique()))
        return(max(for_comparison))
        
    completed_cuts = []
    row_values = []
    for row in df_values:
        if row[0] not in completed_questions:
            heading_row = ['', '', row[df2.columns.get_loc('QuestionTitle')]]
            values.append(heading_row)
    #        answer_list = df.loc[df['Question'] == row[df.columns.get_loc('Question')], 'Answer'].unique()
            answer_row = ['', '']
            answer_list = [i+1 for i in range(get_max_num_of_ans_options()-1)]
            answer_row.extend(answer_list)
            answer_row.append('Desired')
            values.append(answer_row)        
            completed_questions.append(row[df2.columns.get_loc('QuestionTitle')])
        row_values = []
        for i in row[1:]:
            row_values.append(i)
        values.append(row_values)

if append == 'test':
    df = df.groupby(['Attribute', 'Cut', 'QuestionTitle', 'Answer'])['Summary'].last().unstack('QuestionTitle').unstack('Answer').reset_index()
    # currently attribute and cut are considered as part of this level
    # we will need to remove them
    questions = df.columns.get_level_values('QuestionTitle').unique().tolist()
    questions.remove('Attribute')
    questions.remove('Cut')
    import csv
    import os
    values = []
    for question in questions:
        df_out = df[['Attribute', 'Cut', question]]
        df_out = df_out.fillna('')
        df_out.to_csv('temp.csv', encoding='utf_8_sig', index=False)
        with open('temp.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                values.append(row)
        os.remove('temp.csv')
    



#sheetManager.update_values(sheetId=sheetId,
#                           update_range=results_range,
#                           values=values)
