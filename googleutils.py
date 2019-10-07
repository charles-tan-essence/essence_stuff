# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 17:46:16 2019

@author: charles.tan
"""
'''
Create a class to handle authentication
'''

import pickle
import os.path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

class Authenticator():
    '''
    Authenticator Object to handle authentication for you
    Main task of this object is to return the credentials to you
    
    1. Initialize it with your keys (json)
    2. Pass in the scopes you need and get the creds to perform them
    '''
    def __init__(self, keys):
        self.keys = keys

    def get_creds(self, scopes):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.keys, scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
    
        return(creds)

