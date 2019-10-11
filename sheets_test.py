# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 18:22:28 2019

@author: charles.tan
"""

from authenticator import Authenticator
from sheetmanager import SheetManager

sheetId = '1Pk29LAYE-KswZ7cl5dmtE3feJUyH-GAPG3vUHsyKGmc'
sheet_name = 'Testing'


keys = 'credentials.json'
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

authenticator = Authenticator(keys)
creds = authenticator.get_creds(SCOPES)
sheetManager = SheetManager(creds)

requests = []

#requests.append({
#        'updateSpreadsheetProperties': {
#                'properties': {
#                        'title' : 'TEST'
#                        },
#                'fields': 'title'}})

#requests.append({
#        'updateBorders': {
#                'range': {
#                        }}})
#
#
#
#body = {'requests': requests}
#
#sheetManager.batch_update(sheetId=sheetId,
#                          body=body)

spreadsheet_info = sheetManager.get(sheetId=sheetId)
sheet_info = spreadsheet_info['sheets']
for sheet in sheet_info:
    if sheet['properties']['title'] == sheet_name:
        sheet_id = sheet['properties']['sheetId']