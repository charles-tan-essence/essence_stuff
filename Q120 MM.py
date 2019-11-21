# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 15:40:04 2019

@author: charles.tan
"""

import numpy as np
import pandas as pd
import seaborn as sns

from authenticator import Authenticator
from sheetmanager import SheetManager

keys = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

spreadsheetId = '1QbkOSgaHt75LeQY2a9GeUjHajXIHWv3Z-ID7svUPG6w'

authenticator = Authenticator(keys)
creds = authenticator.get_creds(SCOPES)

manager = SheetManager(creds)

# load in the dav figures
dav_df = manager.get_values(sheetId=spreadsheetId,
                            data_range='JP',
                            )

dav_df = dav_df[dav_df['region_name'] != 'null']
dav_df['date'] = pd.to_datetime(dav_df['date'], format='%Y%m%d')
dav_df = dav_df.set_index('region_name')

# load in the cce split
cce_df = manager.get_values(sheetId=spreadsheetId,
                                data_range='CCE Split - JP by region!A2:D50',
                                as_df=True)

cce_df = cce_df[cce_df['region_name'] != 'null']
cce_df = cce_df.set_index('region_name')

# convert the dav list into wide form

dav_df = dav_df.pivot_table(values=['unique_logged_in_dav', 'unique_visitor_dav', 'total'],
                            index='region_name',
                            columns='date')

df = dav_df.merge(cce_df, how='outer', left_index=True, right_index=True)


df.to_csv('out.csv', encoding='utf-8-sig')


