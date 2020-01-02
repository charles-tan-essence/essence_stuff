# -*- coding: utf-8 -*-
"""
Created on Thu Dec 19 11:06:37 2019

@author: charles.tan
"""

import numpy as np
import pandas as pd
from statsmodels.stats.proportion import proportions_ztest as ztest

from authentication.authenticator import Authenticator
from sheets.sheetmanager import SheetManager


keys = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive']

authenticator = Authenticator(keys)
creds = authenticator.get_creds(SCOPES)
manager = SheetManager(creds)
        
output_spreadsheetId = '1DnBLbtXWc05RdYZa4LNAZfCQ4kDgsnNEBGKQiWsyTaY'
output_data_range = 'Results'

raw_data_dict = {
        'spreadsheetId': {
                'ID': '1TpT5R1TBTp4GN7afs2WhA1U-Q79XZlqDGX73lkB23RM',
                'MY': '1b4GhtfV6sII-8MgwQ9nvSQMQsS6XTwZuRpCdWlFUrWA',
                'PH': '1lHPXgXiESwMALLdfrHN4x1gtq-r5EVcfD0OnIIFvykk',
                'TH': '1ip--PDQchRtwREv9fMuECnFuEWooiCDLxW1CEJStzgI',
                },
        'data_range': {
                'ID': 'Indonesia AC CLS Raw Data',
                'MY': 'Malaysia AC CLS Raw Data',
                'PH': 'Philippines AC CLS Raw Data',
                'TH': 'Thailand AC CLS Raw Data',                
                },             
        }

test_floodlight_names = [
        'Type 277047819 (1248666690 S2S - YouTube Music Premium - Global - Sign Up Complete - Android (from YT Music App))',
        'Type 276994469 (1248666690 S2S - YouTube Music Premium - Global - Sign Up Complete - iOS (from YT Music App))',
        ]

base_col_name = 'treatment_user_count'
control_base_col_name = 'control_user_count'
treatment_col_name = 'treatment'
control_col_name = 'scaled_control'
floodlight_col_name = 'conversion_segment'
country_col_name = 'country'
agg_floodlight_col_name = 'Type 276994469 (1248666690 S2S - YouTube Music Premium - Global - Sign Up Complete (from YT Music App))'
        


#raw_data_directory_df = pd.DataFrame(raw_data_dict)
df = pd.DataFrame()
for country in list(raw_data_dict['spreadsheetId'].keys()):   
    df2 = manager.get_values(spreadsheetId=raw_data_dict['spreadsheetId'][country],
                               data_range=raw_data_dict['data_range'][country],
                               )
    df2 = df2.loc[(df2[floodlight_col_name].isin(test_floodlight_names)) &\
                      (df2[country_col_name] == country)]
    if df.empty:
        df = df2
    else:
        df = pd.concat([df, df2], axis=0)
    
df = df[[country_col_name, floodlight_col_name, base_col_name, control_base_col_name,
         control_col_name, treatment_col_name]]

df = df.drop_duplicates(keep='first')

agg_df = df.groupby(country_col_name)[country_col_name,
                   control_col_name, treatment_col_name].sum().reset_index()

agg_df[floodlight_col_name] = agg_floodlight_col_name

agg_df = agg_df.merge(df[[country_col_name, base_col_name, control_base_col_name]].drop_duplicates(keep='first'),
                      how='left', on=country_col_name)

df = pd.concat([df, agg_df])
df = df[[floodlight_col_name, country_col_name, base_col_name,
         control_base_col_name, treatment_col_name, control_col_name]]

df['control_prop'] = df[control_col_name]/df[base_col_name]
df['treatment_prop'] = df[treatment_col_name]/df[base_col_name]
df['abs_lift'] = df['treatment_prop'] - df['control_prop']
df['rel_lift'] = df['abs_lift'] / df['control_prop']
df['p-value'] = df.apply(lambda x: ztest(
        [x[treatment_col_name], x[control_col_name]],
        [x[base_col_name], x[base_col_name]]
    )[1], axis=1)

df['test_significance'] = 'No Lift'
df.loc[(df['abs_lift'] > 0) & (df['p-value'] <= 0.2), 'test_significance'] = 'Directional Lift'
df.loc[(df['abs_lift'] > 0) & (df['p-value'] <= 0.1), 'test_significance'] = 'Significant Lift'
df.loc[(df['abs_lift'] > 0) & (df['p-value'] <= 0.05), 'test_significance'] = 'Strong Significant Lift'
df.loc[(df['abs_lift'] < 0) & (df['p-value'] <= 0.1), 'test_significance'] = 'Negative Lift'

# need to check how to calculate this
df['incremental_conversions'] = df['abs_lift'] * df[base_col_name]

df['sample_size'] = df[base_col_name] + df[control_base_col_name]
df['control_sample_prop'] = df[control_base_col_name] / df['sample_size']


values = []
values.append(df.columns.tolist())
for row in df.values.tolist():
    values.append(row)
    
manager.update_values(spreadsheetId=output_spreadsheetId,
                      update_range=output_data_range,
                      values=values)
