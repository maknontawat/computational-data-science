#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np

data = np.load('monthdata.npz')
totals = data['totals']
counts = data['counts']


# In[2]:


print('Row with lowest total precipitation:')
np.argmin(np.sum(totals, axis = 1))


# In[3]:


print('Average precipitation in each month:')
np.sum(totals, axis = 0) / np.sum(counts, axis = 0)


# In[4]:


print('Average precipitation in each city:')
np.sum(totals, axis = 1) / np.sum(counts, axis = 1)


# In[5]:


print('Quarterly precipitation totals:')
np.sum(np.reshape(totals, (-1, 4, 3)), axis = 2)

