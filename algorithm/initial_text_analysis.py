
# coding: utf-8

# In[2]:

from IPython.core.display import HTML
HTML("<style>.container { width:100% !important; float:center}</style>")


# In[3]:

from __future__ import division, print_function

import os
import glob
import math
import re
import pandas as pd
import numpy as np
# import scipy as sp
import scipy.stats as sps
import matplotlib.pyplot as plt
import seaborn as sns
import requests 
from time import sleep
import json
import re
import datetime
import time

import nltk
from nltk.corpus import stopwords, inaugural, brown
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
from nltk import Text

import wordcloud as wc

import nltk.stem.porter as ptr

import collections
from itertools import groupby


get_ipython().magic(u'matplotlib inline')

sns.set_context('notebook')
sns.set_style('ticks')



# In[36]:

similarity_corpus = Text(inaugural.words())
stops = set(stopwords.words('english'))
    # using a set will make it faster to run through...

punctuation = ['.',',',':','!',';','-','?','"',"'",'(',')','–']   
other = ['deb','hideb','don','didn','twaittry','doesn','thank','heydeb','ve','potatoe']
    
stops_punc = set(stopwords.words('english') + punctuation)

stops_all = set(stopwords.words('english') + punctuation + other)


# In[38]:

mystops = set(stopwords.words('english') + punctuation + other )


# import

# In[5]:

comments = pd.read_csv('/Users/kateliea/Documents/Insight/project/webscrapers/comments_smittenkitchen_100_2.csv', index_col=0)
recipes = pd.read_csv('/Users/kateliea/Documents/Insight/project/webscrapers/recipes_smittenkitchen_100_2.csv', index_col=0)


# sanity check

# In[45]:

recipes.numberofcomments.sum(), len(comments)


# for a given recipe, dump all the comment text into one giant list

# In[49]:

comments.usercomment


# case with just the first recipe in the corpus

# In[ ]:

commentslist = []
for comment in comments.usercomment:
    print(comment)
#     commentslist += [comment.strip('\n').lower()]
#     cleaned = re.sub(r"\n", " ", comment.lower())  
#     commentslist += [re.sub(r"'", "", cleaned)]
    
# #     commentslist += [re.sub(r"\r\n", "  ", comment.lower())]
    
# commentslist_joined = ' '.join(commentslist)


# In[39]:

tokens = word_tokenize(commentslist_joined)
bigrams = ngrams(tokens,2)
trigrams = ngrams(tokens,3)
len(tokens)


# In[43]:

unstopped2 = [word for word in tokens if word not in mystops]
len(unstopped2)


# remove stopwords

# In[42]:

unstopped = [word for word in tokens if word not in stops]
unstopped_nopunctuation = [word for word in tokens if word not in stops_all]
len(unstopped), len(unstopped_nopunctuation)


# stem 

# In[35]:

stemmer = ptr.PorterStemmer()
stems = [stemmer.stem(word) for word in unstopped2]


# some word visualizations

# In[15]:

# take relative word frequencies into account, lower max_font_size
wordcloud = wc.WordCloud(max_font_size=40, relative_scaling=.5).generate(' '.join(unstopped))
plt.figure()
plt.imshow(wordcloud)
plt.axis("off")
plt.show()


# In[35]:

# take relative word frequencies into account, lower max_font_size
wordcloud = wc.WordCloud(max_font_size=30, relative_scaling=0.5, stopwords=wc.STOPWORDS).generate(' '.join(unstopped_nopunctuation))
fig, ax = plt.subplots()
ax.imshow(wordcloud)
ax.set_axis_off()
plt.show()


# In[44]:

wordcloud = wc.WordCloud(relative_scaling=0.5, font_path='/Library/Fonts/Chalkduster',width=2000, height=2000).generate(' '.join(stems))
fig, ax = plt.subplots(figsize=(20,10))
ax.imshow(wordcloud)
ax.set_axis_off()
plt.show()


# In[ ]:



