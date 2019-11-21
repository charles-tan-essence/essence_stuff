# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 10:58:10 2019

@author: charles.tan
"""

import numpy as np
import pandas as pd
from statsmodels.stats.proportion import proportions_ztest

data_path = 'data.csv'
codebook_path = 'codebook.xlsx'

df = pd.read_csv(data_path, encoding='utf_8_sig')

df['Version'] = df['Version'].mask(df['Version'] == 4, '4. Control')
df['Version'] = df['Version'].mask(df['Version'] == 1, '1. Illustration')
df['Version'] = df['Version'].mask(df['Version'] == 2, '2. Colored background')
df['Version'] = df['Version'].mask(df['Version'] == 3, '3. No illustration white background')

qs = ['q3001_1', 'q3001_2', 'q3001_3', 'q3001_4', 'q3001_5',
       'q3002_1', 'q3002_2', 'q3002_3', 'q3002_4', 'q3002_5', 'q3003', 'q3004',
       'q3005', 'q3006_1', 'q3006_2', 'q3006_3', 'q3007', 'q3008', 'q3009',
       'q3010_1', 'q3010_2', 'q3010_3', 'q3010_4', 'q3010_5', 'q3011', 'q3012',
       'q95000', 'q95001', 'q2201', 'q2202', 'q2203', 'q2204', 'q2205',
       'q2206', 'q2401', 'q2402', 'q2403', 'q2404', 'q2405', 'q2406',
       'q7201', 'q7202', 'q7203', 'q7204', 'q7205', 'q7206', 'q7207', 'q7208',
       'q7215', 'q7209', 'q7210', 'q7500', 'q7501']


table = pd.pivot_table(df, values=qs, columns=['Version'], aggfunc='count')

groups = []
col_names = []
for group in table.columns:
    groups.append(group)
    col_names.append(group)
    table[group + ' base'] = len(df[df['Version'] == group])
    col_names.append(group + ' base')

table = table[col_names]

for group in groups:
    if group != '4. Control':
        table[group + ' p-value'] = table.apply(lambda x: proportions_ztest(
                [x[group], x['4. Control']],
                [x[group + ' base'], x['4. Control base']])[1], axis = 1)
        table[group + ' 90% sig'] = 'No Lift'
        table[group + ' 90% sig'] = table[group + ' 90% sig'].mask(table[group + ' p-value'] < .1, 'Significant Lift')
        table[group + ' 95% sig'] = 'No Lift'
        table[group + ' 95% sig'] = table[group + ' 95% sig'].mask(table[group + ' p-value'] < .05, 'Strong Significant Lift')

table.to_csv('result.csv')