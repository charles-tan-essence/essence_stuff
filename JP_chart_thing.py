# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

### change the location of the data
os.chdir(r'C:\Users\charles.tan\Documents\Python Scripts\Data')


### define your file names (for me sheet 20 is MM 1 and sheet 22 is MM 2)
data1 = r'[WIP] GoogleHome 2019 MM 1.csv'
data2 = r'[WIP] GoogleHome 2019 MM 2.csv'

df1 = pd.read_csv(data1).transpose()
df2 = pd.read_csv(data2).transpose()

#print(df1.head())
#print(df2.head())

# get date and total sales for the date

df1['overall_sales'] = df1.sum(axis=1)
df2['overall_sales'] = df2.sum(axis=1)

# drop the header "Prefecture"
df1, df2 = df1.drop('Prefecture'), df2.drop('Prefecture')
# remove Grand Total row
df1= df1.drop('Grand Total')
# further remove headers
df1, df2 = df1.iloc[1:], df2.iloc[1:]

# convert our index to its own dt column
df1['date'] = pd.to_datetime(df1.index)
df2['date'] = pd.to_datetime(df2.index)

# remove unnecessary data since we only want overall
df1 = df1[['date', 'overall_sales']]
df2 = df2[['date', 'overall_sales']]

#build figure
fig = plt.Figure()

plt.plot(df1['date'], df1['overall_sales'])
plt.plot(df2['date'], df2['overall_sales'])
plt.legend(labels = ['Sheet 20', 'Sheet 22'])
plt.title('Overall Sales vs. Date')
plt.show()

# let's see how it looks like if we normalize the sales

def normalize(col):
    return((col - col.mean())/col.std())
    
df1['normalized'] = normalize(df1['overall_sales'])
df2['normalized'] = normalize(df2['overall_sales'])

fig2 = plt.Figure()
plt.plot(df1['date'], df1['normalized'])
plt.plot(df2['date'], df2['normalized'])
plt.legend(labels = ['Sheet 20', 'Sheet 22'])
plt.title('Normalized Overall Sales vs Date')
plt.show()



