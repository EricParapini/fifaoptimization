#!/usr/bin/env python
# coding: utf-8

# # The Data Cleaning Notebook
# 
# This notebook documents the cleaning process for the Fifa 2019 Data. It creates a new csv file in ./data/out/clean.csv

# ## Import necessary libraries

# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

from collections import Counter as counter


# ## Load Data to a data table

# In[2]:


df_fifa = pd.read_csv("../data/data.csv")


# # Manipulation

# ## Convert the value and wage into proper currency

# In[3]:


def value_to_int(df_value):
    try:
        value = float(df_value[1:-1]) # This return 110.5 from €110.5M
        suffix = df_value[-1:] # This return M or K
        if suffix == 'M':
            value = value * 1000000
        elif suffix == 'K':
            value = value * 1000
    except:
        value = 0
    return value

df_fifa['Value'] = df_fifa['Value'].apply(value_to_int)
df_fifa['Wage'] = df_fifa['Wage'].apply(value_to_int)
df_fifa['Release Clause'] = df_fifa['Release Clause'].apply(value_to_int)


# ## Convert the height to CM

# In[4]:


# Inch = 2.54 CM
# Foot = 2.54*12 = 30.48
def convert_to_cm(df_value):
    height = 0
    try:
        feet,inches = str(df_value).split("'",)
        feet = eval(feet)
        inches = eval(inches)
        height = 30.48*feet + 2.54*inches
    except:
        pass #do nothing
    return int(height)

df_fifa['Height'] = df_fifa['Height'].apply(convert_to_cm)


# ## Clean weight data

# In[5]:


def remove_lbs(df_value):
    try:
        weight = int(df_value[0:-3])
    except:
        weight = 0
    return weight

df_fifa['Weight'] = df_fifa['Weight'].apply(remove_lbs)


# ## Cycle through skill columns and add them up

# In[6]:


def evaluate_the_row(x):
    try:
        return eval(x)
    except:
        return 0

# 26 Positions need addition
for i in range(28,54):
    df_fifa.iloc[:,i] = df_fifa.iloc[:,i].apply(evaluate_the_row)


# ## Remove Cells where key items are 0

# In[7]:


df_fifa = df_fifa[df_fifa.Value != 0]
df_fifa = df_fifa[df_fifa.Overall != 0]
df_fifa = df_fifa[df_fifa.Height != 0]
df_fifa = df_fifa[df_fifa.Weight != 0]


# ## Add new column: Create a variable with a classified position

# In[8]:


def classify_position(df_value):
    if(df_value == 'GK'):
        return 1
    elif(df_value in ['RCB', 'CB', 'LCB', 'LB', 'RB', 'RWB', 'LWB']):
        return 2
    elif(df_value in ['RCM', 'LCM', 'LDM', 'CDM', 'CAM', 'RM', 'LAM', 'LM', 'RDM', 'CM', 'RAM']):
        return 3
    elif(df_value in ['RF', 'LF', 'ST', 'LW', 'RS', 'LS', 'RW', 'CF']):
        return 4
    return 0

df_fifa['PositionCode'] = df_fifa['Position'].apply(classify_position)


# # Error Checking

# ## Reviewing Value

# In[9]:


df_fifa['Value'].describe().apply(lambda x: format(x, 'f'))


# ## Reviewing Wage

# In[10]:


df_fifa['Wage'].describe().apply(lambda x: format(x, 'f'))


# ## Check Positions were added correctly

# In[11]:


df_fifa.iloc[:,28:54]


# # Write to CSV

# In[12]:


export_csv = df_fifa.to_csv(r'../out/clean.csv', index=None, header=True)

