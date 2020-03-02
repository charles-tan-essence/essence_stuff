# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 15:06:43 2020

@author: charles.tan
"""
import pandas as pd
from googleapiclient.discovery import build

from authentication.authenticator import Authenticator
from sheets.sheetmanager import SheetManager

keys = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive']

folder_id = '1Eri3yVNP1zOWkz9xxFOPRlmOtKurvJ-Y'

authenticator = Authenticator(keys)
creds = authenticator.get_creds(SCOPES)
manager = SheetManager(creds)

resource = build('drive', 'v3', credentials=creds).files()

request = resource.list(corpora='user',
                        q="'"+folder_id+"' in parents")

response = request.execute()

files = response['files']

big_df = pd.DataFrame()

for file in files:
    df = manager.get_values(sheetId=file['id'],
                            data_range='LIBRA_BLS_Data')
    if big_df.empty:
        big_df = df
    else:
        big_df = pd.concat([big_df, df])

print(big_df)