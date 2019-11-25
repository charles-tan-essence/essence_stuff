# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 15:02:56 2019

@author: charles.tan
"""
import streamlit as st
import numpy as np
import pandas as pd

from authenticator import Authenticator
from sheetmanager import SheetManager

keys = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

spreadsheetId = '1rlc8Wltr15SCLie4QrbiZjNQXSkD7l19dbBixdhTuCg'
data_range = 'Results'

authenticator = Authenticator(keys)
creds = authenticator.get_creds(SCOPES)

manager = SheetManager(creds)

values = manager.get_values(sheetId=spreadsheetId,
                            data_range=data_range)
