
# coding: utf-8

# In[2]:

from IPython.core.display import HTML
HTML("<style>.container { width:90% !important; float:left}</style>")


# In[248]:

from __future__ import division, print_function

import os
import glob
import math
import re
from collections import Counter
import datetime
from itertools import groupby

import pandas as pd
import numpy as np
import sklearn as skl
# import scipy as sp
# import scipy.stats as sps
import matplotlib.pyplot as plt
import seaborn as sns
import wordcloud as wc


import nltk
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
# from nltk import Text



# In[28]:

porter = PorterStemmer()

get_ipython().magic(u'matplotlib inline')

sns.set_context('notebook')
sns.set_style('ticks')


# In[208]:

stops = set(stopwords.words('english'))
    # using a set will make it faster to run through...

punctuation = ['.',',',':','!',';','-','?','"',"'",'(',')','—']   
other = ['deb','hideb','don','didn','twaittry','doesn','thank','heydeb','ve', "i've", "i'v"]
    
stops_punc = set(stopwords.words('english') + punctuation)

mystops = stopwords.words('english') + punctuation + other
mystops_set = set(stopwords.words('english') + punctuation + other)


# import & sanity check

# In[275]:

comments = pd.read_csv('/Users/kateliea/Documents/Insight/project/webscrapers/comments_smittenkitchen_100.csv', index_col=0)
recipes = pd.read_csv('/Users/kateliea/Documents/Insight/project/webscrapers/recipes_smittenkitchen_100.csv', index_col=0)

recipes.numberofcomments.sum(), len(comments), len(recipes), comments.columns


# a bit of cleaning - remove any comments where there is not comment text

# In[276]:

# remove any comments with no comment text
comments = comments[pd.notnull(comments.usercomment)]

# replace NaN usernames with 'anon'
comments['username'].fillna('anon', inplace=True)

# sanity check
recipes.numberofcomments.sum(), len(comments), len(recipes)


# tokenize 

# In[277]:

def make_lowercase(comment):
    return remove_newlines(comment.lower())

def tokenize(comment):
    comment = remove_newlines(comment)
    return [word for word in word_tokenize(remove_newlines(comment).lower()) if word not in mystops]
    
def tokenize_stem(comment):
    tokens = word_tokenize(remove_newlines(comment).lower())
    return [porter.stem(word) for word in tokens if word not in mystops]

def remove_newlines(comment):    
    return re.sub(r"\n", " ", comment)


# In[278]:

comments['usercomment'] = comments.usercomment.apply(remove_newlines)
comments['usercomment_lower'] = comments.usercomment.apply(make_lowercase)
comments['tokens'] = comments.usercomment.apply(tokenize)
comments['tokens_stemmed'] = comments.usercomment.apply(tokenize_stem)


# In[256]:

commentslist = []
for comment in comments.tokens:
    commentslist += [' '.join(comment)]
#     commentslist += [comment.strip('\n').lower()]
#     cleaned = re.sub(r"\n", " ", comment.lower())  
#     commentslist += [re.sub(r"'", "", cleaned)]
    
# #     commentslist += [re.sub(r"\r\n", "  ", comment.lower())]
    
commentslist_joined = ' '.join(commentslist)
commentslist_joined


# In[ ]:




# In[265]:

comments[comments.usercomment.str.contains('suggest')]


# In[274]:

comments[comments.usercomment.str.contains('omitted')]


# testing sentence map

# In[280]:

test = comments.loc[:,['usercomment','username','commentID','recipenumber']]
test2 = test.loc[:10,:]


# In[289]:

def tokenize_sentences(comment):
    return nltk.sent_tokenize(remove_newlines(comment.lower()))
    
def make_new_columns(comment):
    for i, elem in enumerate(tokenize_sentences(comment)):
        pass
        

pd.concat([Series(row['var2'], row['var1'].split(',')) for _, row in a.iterrows()]).reset_index()
# In[293]:

pd.concat([pd.Series(row['commentID'], tokenize_sentences((row['usercomment']))) for _, row in test2.iterrows()]).reset_index


# In[302]:

pd.concat([pd.DataFrame(row[['username','commentID','recipenumber']], tokenize_sentences((row['usercomment']))) for _, row in test2.iterrows()]).reset_index


# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:




# word relevancy - tf-idf

# In[213]:

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
count = CountVectorizer()
tfidf = TfidfTransformer()


# In[223]:

docs = comments.usercomment.as_matrix()


# In[240]:

bagofwords = count.fit_transform(docs)


# In[247]:

count = Counter()
print(count.most_common)


# In[269]:

count.vocabulary_['instead']


# In[236]:

tf = tfidf.fit_transform(count.fit_transform(docs)).toarray()


# In[246]:

tf[tf[21285]>0]


# In[229]:

len(count.vocabulary_)


# In[235]:

docs_clean = comments.tokens_stemmed
docs_clean


# In[234]:

bagofwords = count.fit_transform(docs_clean)


# In[ ]:




# some word visualizations
# take relative word frequencies into account, lower max_font_size
wordcloud = wc.WordCloud(max_font_size=40, relative_scaling=.5).generate(' '.join(unstopped))
plt.figure()
plt.imshow(wordcloud)
plt.axis("off")
plt.show()# take relative word frequencies into account, lower max_font_size
wordcloud = wc.WordCloud(max_font_size=30, relative_scaling=0.5, stopwords=wc.STOPWORDS).generate(' '.join(unstopped_nopunctuation))
fig, ax = plt.subplots()
ax.imshow(wordcloud)
ax.set_axis_off()
plt.show()wordcloud = wc.WordCloud(relative_scaling=0.5, font_path='/Library/Fonts/Chalkduster',width=2000, height=2000).generate(' '.join(stems))
fig, ax = plt.subplots(figsize=(20,10))
ax.imshow(wordcloud)
ax.set_axis_off()
plt.show()
# In[ ]:



