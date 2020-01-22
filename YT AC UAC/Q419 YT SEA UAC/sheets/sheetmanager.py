# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 16:19:49 2019

@author: charles.tan
"""

from googleapiclient.discovery import build
import pandas as pd
import json

class SheetManager():
    def __init__(self, creds):
        self.creds = creds
        self.resource = build('sheets', 'v4', credentials=creds).spreadsheets()
        
    def get_values(self, spreadsheetId, data_range, as_df = True):
        resource = self.resource.values()
        request = resource.get(spreadsheetId=spreadsheetId, range=data_range,
                               valueRenderOption='UNFORMATTED_VALUE',
                               dateTimeRenderOption='FORMATTED_STRING')
        response = request.execute()
        values = response['values']
        if as_df:
            return(pd.DataFrame(values[1:], columns=values[0]))
        else:
            return(values)
    
    def update_values(self, spreadsheetId, update_range, values):
        resource = self.resource.values()
        request = resource.update(spreadsheetId=spreadsheetId,
                                  range=update_range,
                                  body={'values': values},
                                  valueInputOption='USER_ENTERED')
        response = request.execute()
        return(response)
    

    def append_values(self, spreadsheetId, append_range, values):
        resource = self.resource.values()
        request = resource.append(spreadsheetId=spreadsheetId,
                                  range=append_range,
                                  body={'values': values},
                                  valueInputOption='USER_ENTERED')
        response = request.execute()
        return(response)


    # instead of batch update which is quite unwieldy
    # try to create functions for each task
    # such as creating borders or something    
    def batch_update(self, spreadsheetId, body):
        resource = self.resource.batchUpdate(spreadsheetId=spreadsheetId,
                                             body=body)
        resource.execute()
        
    def get(self, spreadsheetId, ranges=None):
        resource = self.resource.get(spreadsheetId=spreadsheetId,
                                     ranges=ranges)
        return(resource.execute())
 
    def get_existing_sheets(self, spreadsheetId, ranges=None):
        spreadsheet_data = self.get(spreadsheetId=spreadsheetId, ranges=ranges)
        return(spreadsheet_data['sheets'])
    
    def get_sheet_id(self, spreadsheetId, sheet_name, ranges=None):
        spreadsheet_data = self.get(spreadsheetId=spreadsheetId, ranges=ranges)
        sheets_properties = spreadsheet_data['sheets']
        for sheet_properties in sheets_properties:
            if sheet_properties['properties']['title'] == sheet_name:
                return(sheet_properties['properties']['sheetId'])
        return(None)
    
    def get_existing_sheets_names(self, spreadsheetId):
        sheet_names = []
        sheets_properties = self.get_existing_sheets(spreadsheetId=spreadsheetId)
        for sheet_properties in sheets_properties:
            sheet_names.append(sheet_properties['properties']['title'])
        return(sheet_names)
    
    def add_sheet(self, spreadsheetId, sheet_name):       
        body = {'requests': [
                    {'addSheet': {
                        'properties':{
                                'title': sheet_name,
                                }
                        }
                    }
                        ]
                }
        if sheet_name not in self.get_existing_sheets_names(spreadsheetId=spreadsheetId):
            self.batch_update(spreadsheetId=spreadsheetId, body=body)
        else:
            print('Sheet with same name already exists. No need sheet created.')
                