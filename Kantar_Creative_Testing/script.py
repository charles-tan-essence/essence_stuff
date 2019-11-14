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

df['Version'] = df['Version'].mask(df['Version'] == 4, 'Control')
df['Version'] = df['Version'].mask(df['Version'] == 1, 'Illustration')
df['Version'] = df['Version'].mask(df['Version'] == 2, 'Colored background')
df['Version'] = df['Version'].mask(df['Version'] == 3, 'No illustration white background')

qs = ['q3001_1', 'q3001_2', 'q3001_3']


table = pd.pivot_table(df, values=qs, columns=['Version'], aggfunc='count')

for group in table.columns:
    table[group + ' base'] = len(df[df['Version'] == group])

table['results'] = table.apply(lambda x: proportions_ztest([x['Illustration'], x['Control']], [x['Illustration base'], x['Control base']])[1], axis=1)
    

table.to_csv('result.csv')