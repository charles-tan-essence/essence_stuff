# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 16:03:31 2019

@author: charles.tan

format to create requests and execute them:
https://developers.google.com/sheets/api/guides/batchupdate#example
sample recipes:
https://developers.google.com/sheets/api/samples/reading
more documentation of potential requests:
https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/request

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

# get Scrutineer Results
df = sheetManager.get_values(sheetId=sheetId, data_range=data_range)
df = df.sort_values(['Question', 'Attribute', 'Cut', 'Answer'])
# calculate Abs Lift
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

# select the columns we need and write them to our Lookup Tab
lookup_df = lookup_df[['identifier', 'Significance', 'Summary', 'Conv_Con', 'Abs_Lift']]
lookup_values = []
lookup_values.append(lookup_df.columns.to_list())
for row in lookup_df.values.tolist():
    lookup_values.append(row)
    
sheetManager.update_values(sheetId=sheetId,
                           update_range=lookup_range,
                           values=lookup_values)

# now we start building the list of lists for our magic template tab
values = []

# create "header" area
questions = df.groupby(['Question', 'QuestionTitle', 'Answer'])['AnswerValue'].last()
questions = questions.reset_index()

buffer_size = 2 # so there is room for the attribute and cuts columns
questions_row = []
answers_row = []
metric_row = []
for x in range(buffer_size):
    questions_row.append('')
    answers_row.append('')
    metric_row.append('')

for question in questions['QuestionTitle'].unique():
    # get the metric (e.g. Awareness) for each question
    metric = df.loc[df['QuestionTitle'] == question, 'QuestionCategory'].unique()[0]
    # find out how many times we need to repeat the question (based on the number of answer options)
    gaps = len(questions.loc[questions['QuestionTitle'] == question, 'Answer'].unique())-1
    questions_row.append(question)
    for gap in range(gaps):
        questions_row.append(question)
    # get the answers and write each one
    answers = questions.loc[questions['QuestionTitle'] == question, 'Answer'].str.cat(questions.loc[questions['QuestionTitle'] == question, 'AnswerValue'], sep=': ')
    for answer in answers:
        answers_row.append(answer)
        metric_row.append(metric)

# append each list to our values list
# header portion complete!
values.append(questions_row)
values.append(answers_row)
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

baseline_col = lookup_df.columns.get_loc('Conv_Con') + 1    
summary_col = lookup_df.columns.get_loc('Summary') + 1
#results_formula = '=vlookup(concatenate(index(indirect(address(row(), 1, 3, TRUE))),"|",index(indirect(address(row(), 2, 3, TRUE))),"|",index(indirect(address(1,column(),2,TRUE))),"|",index(indirect(address(2,column(),2,TRUE)))), ScrutineerLookup!A:Z, '+str(summary_col)+', false)'
results_formula = '=CONCATENATE(INDIRECT(ADDRESS(ROW()-2,1,1,1)),"|",INDIRECT(ADDRESS(ROW()-2,2,1,1)),"|",INDIRECT(ADDRESS(1,COLUMN(),1,1)),"|",INDIRECT(ADDRESS(2,COLUMN(),1,1)))'
# for the sample size formula,
# each attribute/cut pair will have the same sample size throughout all the qns and ans
# so we just need to get the first one
sample_size_formula = 'Sample Size Placeholder'
baselines_formula = '=vlookup(CONCATENATE(INDIRECT(ADDRESS(ROW()-1,1,1,1)),"|",INDIRECT(ADDRESS(ROW()-1,2,1,1)),"|",INDIRECT(ADDRESS(1,COLUMN(),1,1)),"|",INDIRECT(ADDRESS(2,COLUMN(),1,1))),ScrutineerLookup!A:Z,'+str(baseline_col)+',false)'

# MAIN BODY
# get all the possible attribute/cut combinations
cuts = df.groupby(['Attribute', 'Cut'])['Significance'].last().reset_index()
cuts_list = cuts[['Attribute', 'Cut']].values.tolist()

# get the length of the header row so we know how many times to write the formula
len_of_header = len(answers_row)
len_to_write = len_of_header - buffer_size

for row in cuts_list:
    # create a row for each attribute/cut pair
    pair = []
    for item in row:
        pair.append(item)
    values.append(pair)
    # create a row for the baselines
    baselines = ['', 'Baseline']
    for x in range(len_to_write):
        baselines.append(baselines_formula)
    values.append(baselines)
    # create a row for the results, with sample size in front
    results = ['Sample Size:', sample_size_formula]
    for x in range(len_to_write):
        results.append(results_formula)
    values.append(results)

#import csv
#with open('test.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
#    writer = csv.writer(csvfile)
#    for row in values:
#        writer.writerow(row)

sheetManager.update_values(sheetId=sheetId,
                           update_range=results_range,
                           values=values)