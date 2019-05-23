#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import re
import matplotlib.pyplot as plt

from pandas.plotting import register_matplotlib_converters
from scipy import stats

register_matplotlib_converters()


# In[2]:


def to_timestamp(date):
    return date.timestamp()

def extract_rating(text):
    r = r'(\d+(\.\d+)?)/10'
    m = re.search(r, text)
    return float(m.group(0)[:-3]) if m else None


# In[3]:


data = pd.read_csv('dog_rates_tweets.csv', parse_dates=[1])

data['timestamp'] = data['created_at'].apply(to_timestamp)
data['rating'] = data['text'].apply(extract_rating)
data = data[(data['rating'].notnull()) & (data['rating'] < 25.0)]

fit = stats.linregress(data['timestamp'], data['rating'])
data['prediction'] = fit.intercept + fit.slope*data['timestamp']


# In[4]:


data


# In[5]:


fit.slope, fit.intercept


# In[6]:


plt.figure(figsize=(10, 5))
plt.xticks(rotation=25)
plt.xlabel('Dates')
plt.ylabel('Ratings')
plt.plot(data['created_at'], data['rating'], 'b.', alpha=0.5)
plt.plot(data['created_at'], data['prediction'], 'r-', linewidth=3)
plt.show()

