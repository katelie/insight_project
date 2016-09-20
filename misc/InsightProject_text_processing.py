
# coding: utf-8

# In[1]:

from IPython.core.display import HTML
HTML("<style>.container { width:90% !important; float:center}</style>")


# In[2]:

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

import time


# In[3]:

porter = PorterStemmer()

get_ipython().magic(u'matplotlib inline')

sns.set_context('notebook')
sns.set_style('ticks')


# In[4]:

stops = set(stopwords.words('english'))
    # using a set will make it faster to run through...

punctuation = ['.',',',':','!',';','-','?','"',"'",'(',')','—']   
other = ['ve', "i've", "i'v", 'i’ll', 'i’ve', 'i’v']  # 'deb','hideb','don','didn','twaittry','doesn','thank','heydeb',
    
stops_punc = set(stopwords.words('english') + punctuation)

mystops = stopwords.words('english') + punctuation + other
mystops_set = set(stopwords.words('english') + punctuation + other)


# In[52]:

def tokenize_sentences(comment):
    return nltk.sent_tokenize(remove_newlines(comment.lower()))
    
    
def make_sentences_frame(frame, identifier, paragraph, how='merge'):
    sentences = pd.concat([pd.Series(row[identifier], tokenize_sentences((row[paragraph]))) for _, row in frame.iterrows()]).reset_index()
    sentences.columns = ['sentence', identifier]
    
    if how == 'merge':
        return sentences.merge(frame, left_on=identifier, right_on=identifier, how='outer', sort=False, suffixes=('_l','_r')) 
    elif how == 'nomerge': 
        return sentences
    else: 
        return sentences.merge(frame, left_on=identifier, right_on=identifier, how='outer', sort=False, suffixes=('_l','_r')) 

# slightly faster version
def make_sentences_frame2(frame, identifier, paragraph, how='merge'):
    sentences = pd.DataFrame((tokenize_sentences(row[paragraph]) for _, row in frame.iterrows()), index=frame[identifier]).stack()
    sentences = sentences.reset_index()[[0, identifier]] # var1 variable is currently labeled 0
    sentences.columns = ['sentence', identifier] # renaming var1
    
    if how == 'merge':
        return sentences.merge(frame, left_on=identifier, right_on=identifier, how='outer', sort=False, suffixes=('_l','_r')) 
    elif how == 'nomerge': 
        return sentences
    else: 
        return sentences.merge(frame, left_on=identifier, right_on=identifier, how='outer', sort=False, suffixes=('_l','_r')) 


def make_lowercase(comment):
    return remove_newlines(comment.lower())

def tokenize(comment):
    comment = remove_newlines(comment)
    if comment == []:
        return None
    else: 
        return [word for word in word_tokenize(remove_newlines(comment).lower()) if word not in mystops]
    
def tokenize_stem(comment):
    tokens = word_tokenize(remove_newlines(comment).lower())
    if tokens == []:
        return None
    else: 
        return [porter.stem(word) for word in tokens if word not in mystops]

def remove_newlines(comment):    
    return re.sub(r"\n", " ", comment)


# import & sanity check

# In[47]:

comments = pd.read_csv('/Users/kateliea/Documents/Insight/project/webscrapers/comments_smittenkitchen_100.csv', index_col=0)
recipes = pd.read_csv('/Users/kateliea/Documents/Insight/project/webscrapers/recipes_smittenkitchen_100.csv', index_col=0)

comments_classified = pd.read_csv('comments_classified_SK_filtered2000')

comments.columns, len(comments), len(recipes), recipes.numberofcomments.sum()


# a bit of cleaning - remove any comments where there is not comment text

# In[48]:

comments['commentID'] = comments.index

# remove any comments with no comment text
comments = comments[pd.notnull(comments.usercomment)]

# replace NaN usernames with 'anon'
comments['username'].fillna('anon', inplace=True)

# sanity check
recipes.numberofcomments.sum(), len(comments), len(recipes)


# ### make new dataframe with sentences separated

# In[49]:

comments_sentences = make_sentences_frame2(comments, 'commentID','usercomment',how='merge')
comments_sentences = comments_sentences.dropna()
comments_sentences = comments_sentences.drop([],axis=0)


# ### tokenize 

# In[50]:

comments_sentences['usercomment'] = comments_sentences.usercomment.apply(remove_newlines)
comments_sentences['usercomment_lower'] = comments_sentences.usercomment.apply(make_lowercase)


# In[ ]:

comments_sentences['tokens'] = comments_sentences.usercomment.apply(tokenize)
comments_sentences['tokens_stemmed'] = comments_sentences.usercomment.apply(tokenize_stem)


# In[ ]:

comments_sentences['sentence'] = comments_sentences.sentence.apply(tokenize)
comments_sentences = comments_sentences.dropna()
comments_sentences = comments_sentences.drop([],axis=0)


# In[ ]:

comments_sentences['sentence_stemmed'] = comments_sentences.sentence.apply(tokenize_stem)
comments_sentences = comments_sentences.dropna()
comments_sentences = comments_sentences.drop([],axis=0)


# In[ ]:




# In[ ]:




# In[ ]:




# In[ ]:

commentslist = []
for comment in comments.tokens:
    commentslist += [' '.join(comment)]
#     commentslist += [comment.strip('\n').lower()]
#     cleaned = re.sub(r"\n", " ", comment.lower())  
#     commentslist += [re.sub(r"'", "", cleaned)]
    
# #     commentslist += [re.sub(r"\r\n", "  ", comment.lower())]
    
commentslist_joined = ' '.join(commentslist)
# commentslist_joined


# In[ ]:

comments[comments.usercomment.str.contains('suggest')]


# In[ ]:

comments[comments.usercomment.str.contains('omitted')]


# testing and timing 
# test = comments.loc[:,['usercomment','username','commentID','recipenumber']]
test2 = comments.loc[:1000,:]start = time.clock()
a = make_sentences_frame(test2, 'commentID','usercomment',how='nomerge')
end = time.clock()
print(end-start)start = time.clock()
a = make_sentences_frame2(test2, 'commentID','usercomment',how='nomerge')
end = time.clock()
print(end-start)
# testing sentence map

# In[ ]:



sentences = pd.concat([pd.Series(row['commentID'], tokenize_sentences((row['usercomment']))) for _, row in test2.iterrows()]).reset_index()
sentences.columns = ['usersentence','commentID']
sentences2 = sentences.merge(frame, left_on='commentID', right_on='commentID', how='outer')



pd.concat([Series(row['var2'], row['var1'].split(',')) for _, row in a.iterrows()]).reset_index()

sentences = pd.concat([pd.Series(row['commentID'], tokenize_sentences((row['usercomment'])), name='commentID') for _, row in test2.iterrows()]).reset_index()

sentences.join(test2, on='commentID', how='outer',lsuffix='_L')

# alternative approach
b = DataFrame(a.var1.str.split(',').tolist(), index=a.var2).stack()
b = b.reset_index()[[0, 'var2']] # var1 variable is currently labeled 0
b.columns = ['var1', 'var2'] # renaming var1
# word relevancy - tf-idf

# In[ ]:

from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
count = CountVectorizer()
tfidf = TfidfTransformer()


# In[ ]:

docs = comments.usercomment.as_matrix()


# In[ ]:

bagofwords = count.fit_transform(docs)


# In[ ]:

count = Counter()
print(count.most_common)


# In[ ]:

count.vocabulary_['instead']


# In[ ]:

tf = tfidf.fit_transform(count.fit_transform(docs)).toarray()


# In[ ]:

tf[tf[21285]>0]


# In[ ]:

len(count.vocabulary_)


# In[ ]:

docs_clean = comments.tokens_stemmed
docs_clean


# In[ ]:

bagofwords = count.fit_transform(docs_clean)

