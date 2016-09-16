
# coding: utf-8

# In[117]:

from IPython.core.display import HTML
HTML("<style>.container { width:90% !important; }</style>")


# In[118]:

from __future__ import division, print_function

from sys import argv
import os
import glob
import math
import pandas as pd
import numpy as np
import scipy as sp
import scipy.stats as sps
import matplotlib.pyplot as plt
import seaborn as sns
import simplejson as jsn
import requests 
from time import sleep
import json
import re
from urllib import urlretrieve, urlopen 
from bs4 import BeautifulSoup

import statsmodels.api as sm
from statsmodels.compat import lmap

get_ipython().magic(u'matplotlib inline')

sns.set_context('notebook')
sns.set_style('ticks')


# In[119]:

url = 'http://cooking.nytimes.com/recipes/'


# In[120]:

def openPage(url):
    try: 
        html = urlopen(url)
    except HTTPError as e: 
        return None

    try:
        pageData = BeautifulSoup(html,"html.parser")
    except AttributeError as e: 
        return None

    return pageData


# def getTitle(page_number):
#     soup = openPage(url+page_number)
#     try: 
#         recipename = soup.head.title.text # soup.find('head').find('title')
#     except AttributeError as e:
#         return None
#     return recipename

def Title(soup):
    try: 
        recipename = soup.head.title.text # soup.find('head').find('title')
    except AttributeError as e:
        return None
    return str(recipename)



# def getIngredients(page_number):
#     soup = openPage(url+page_number)
#     try: 
#         ingredients = soup.find('body').find('ul', {'class':'recipe-ingredients'}).findAll('span',{'ingredient-name':''})
#     except AttributeError as e:
#         return None
#     return ingredients

def Ingredients(soup):
    try: 
        ingredients = soup.find('body').find('ul', {'class':'recipe-ingredients'}).findAll('span',{'class':'ingredient-name'})
    except AttributeError as e:
        return None
    return ingredients



# def getDescription(page_number):
#     soup = openPage(url+page_number)
#     try: 
#         description = soup.find('div',{'class':'topnote'}).find('p').string
#     except AttributeError as e:
#         return None
#     return description

def Description(soup):
    try: 
        description = soup.find('div',{'class':'topnote'}).find('p').string
    except AttributeError as e:
        return None
    return str(description)




# def getPgInfo(page_number):
#     soup = openPage(url+page_number)
    
#     try: 
#         recipename = soup.find('head').find('title')
#     except AttributeError as e:
#         return None
    
#     try: 
#         description = soup.find('div',{'class':'topnote'}).find('p').string
#     except AttributeError as e:
#         return None
    
    
#     return recipename, description
    


# In[121]:

def getEverything(page_number):
    soup = openPage(url+page_number)
    recipe_dict = {Title(data) : {'ingredients':Ingredients(data), 'description':Description(data)}}
    return recipe_dict


# In[122]:

elem


# In[123]:

data = openPage(url+'1016788')


# In[108]:

data = {}

for elem in range(10,100):
    data.update(getEverything(str(elem)))


# In[102]:

b = {Title(data) : {'ingredients':Ingredients(data), 'description':Description(data)}}


# In[124]:

data


# In[133]:

a = getEverything('1016000')
b = getEverything('1016787')


# In[132]:

b


# In[ ]:



