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


# create "header" area
questions = df.groupby(['Question', 'QuestionTitle', 'Answer'])['AnswerValue'].last()

questions = questions.reset_index()

values = []
questions_row = []
answers_row = []

for question in questions['QuestionTitle'].unique():
    gaps = len(questions.loc[questions['QuestionTitle'] == question, 'Answer'].unique())-1
    questions_row.append(question)
    for gap in range(gaps):
        questions_row.append('')
    answers = questions.loc[questions['QuestionTitle'] == question, 'Answer'].str.cat(questions.loc[questions['QuestionTitle'] == question, 'AnswerValue'], sep=': ')
    for answer in answers:
        answers_row.append(answer)

values.append(questions_row)
values.append(answers_row)

#import csv
#with open('preview.csv', 'w', encoding='utf-8-sig', newline='') as csvfile:
#    writer = csv.writer(csvfile)
#    for row in values:
#        writer.writerow(row)


#sheetManager.update_values(sheetId=sheetId,
#                           update_range=results_range,
#                           values=values)
