# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 10:58:10 2019

@author: charles.tan
"""

import numpy as np
import pandas as pd

data_path = 'data.xlsx'

df = pd.read_excel(data_path)

print(df.head())