# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 16:19:49 2019

@author: charles.tan
"""

from googleapiclient.discovery import build
import pandas as pd

class SheetManager():
    def __init__(self, creds):
        self.creds = creds
        self.resource = build('sheets', 'v4', credentials=creds).spreadsheets()
        
    def get_values(self, spreadsheetId, data_range, as_df = True):
        resource = self.resource.values()
        request = resource.get(spreadsheetId=spreadsheetId, range=data_range,
                               valueRenderOption='UNFORMATTED_VALUE')
        response = request.execute()
        values = response['values']
#        # preview
#        if (len(values) >= 6):
#            print(values[:6])
#        else:
#            print(values[:len(values)])
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
        
    def batch_update(self, spreadsheetId, body):
        resource = self.resource.batchUpdate(spreadsheetId=spreadsheetId,
                                             body=body)
        resource.execute()
        
    def get(self, spreadsheetId, ranges=None):
        resource = self.resource.get(spreadsheetId=spreadsheetId,
                                     ranges=ranges)
        return(resource.execute())