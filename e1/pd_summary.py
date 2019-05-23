#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd

totals = pd.read_csv('totals.csv').set_index(keys=['name'])
counts = pd.read_csv('counts.csv').set_index(keys=['name'])


# In[2]:


print('City with lowest total precipitation:')
pd.Series.idxmin(pd.DataFrame.sum(totals, axis=1))


# In[3]:


print('Average precipitation in each month:')
pd.DataFrame.sum(totals, axis=0) / pd.DataFrame.sum(counts, axis=0)


# In[4]:


print('Average precipitation in each city:')
pd.DataFrame.sum(totals, axis=1) / pd.DataFrame.sum(counts, axis=1)
