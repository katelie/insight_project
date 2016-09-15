
# coding: utf-8

# In[1]:

from IPython.core.display import HTML
HTML("<style>.container { width:100% !important; float:center}</style>")


# In[2]:

from __future__ import division, print_function

# from sys import argv
# import os
# import glob
# import math
import re
import pandas as pd
import numpy as np
# import scipy as sp
# import scipy.stats as sps
# import matplotlib.pyplot as plt
# import seaborn as sns
# import simplejson as jsn
import requests 
from time import sleep
import json
import re
from urllib import urlretrieve, urlopen 
from bs4 import BeautifulSoup

# %matplotlib inline

# sns.set_context('notebook')
# sns.set_style('ticks')


# In[3]:

url = 'https://smittenkitchen.com'
sk_sitemap = 'https://smittenkitchen.com/sitemap.xml'

# for SK, recipes are listed in <url>/yr/mo/<name> format, other aggregations/lists do not have this same formatting 
sk_regex = 'https://smittenkitchen.com/[0-9]{3,}.*'


# In[28]:

def OpenPage(url):
    try: 
        html = urlopen(url)
    except HTTPError as e: 
        return None

    try:
        pageData = BeautifulSoup(html, 'lxml') #,"html.parser")
    except AttributeError as e: 
        return None

    return pageData


def ScrapeSitemap(url):
    '''returns urls under <loc> tag in sitemap, as text string'''
    sitemap = OpenPage(url)
    taglist = sitemap.findAll('loc')
    urllist = [elem.text for elem in taglist]
    return urllist


def URLFilter(urllist, expression):
    '''filters url list via regex to eliminate non-recipe pages (category aggregations, misc posts, etc)'''
    matches = []
    for url in urllist: 
        match = re.match(expression, url)
        if match: 
            matches += [match.group(0)]
    return matches


def TryFind(search):
    try: 
        result = search
    except AttributeError as e: 
        return None
    return result


# In[129]:

def GetEntryDescription(soup):
    recipe_text = []
    for paragraph in TryFind(soup1.select('div.smittenkitchen-print-hide > p')):
        expression = '.*(\s)*.*[Aa]go:.*'
        if paragraph.a:
            text = paragraph.get_text()
            match = re.match(expression, text)
            if match: 
                continue
            else: recipe_text += paragraph
        
        else: recipe_text += paragraph
            
    return recipe_text


# In[318]:

def GetRecipe_old(soup):
    '''get directions & ingredients separately'''
    
    intro, ingredients, directions, meta = [], [], [], []
    
    for item in TryFind(soup.select('div.entry-content > p')):
        if item.br:
            ingredients += [item.get_text()]
        else: 
            directions += [item.get_text()]
    meta += ['NA']
    intro += ['NA']
        
            
    return intro, ingredients, directions, meta


def GetRecipe_new(soup):
    '''get directions & ingredients separately'''
    intro = []
    for item in TryFind(soup1.findAll('div',{'class':'jetpack-recipe-notes'})):
        if item.a: 
            intro += item.get_text()
        else: intro += item.get_text()
    intro = ''.join(intro)
    
    ingredients = []    
    for item in TryFind(soup1.findAll('li',{'class':'jetpack-recipe-ingredient'})):
        if item.a: 
            ingredients += [item.get_text()]
        else: ingredients += [item.get_text()]

            
    directions = []
    for item in TryFind(soup1.find('div',{'class':'jetpack-recipe-directions'}).findAll('p')):
        if item.a: 
            directions += [item.get_text()]
        else: directions += [item.get_text()]

            
    recipe_meta = {}
    recipe_meta['servings'] = TryFind(soup1.find('li',{'class':'jetpack-recipe-servings'}).get_text())
    recipe_meta['time'] = TryFind(soup1.find('li',{'class':'jetpack-recipe-time'}).get_text())
            
    return intro, ingredients, directions, recipe_meta



def GetRecipe(soup):
    '''SK underwent a site redesign; find the right way to scrape the recipe data'''
    
    if TryFind(soup.find('div',{'class':'hrecipe jetpack-recipe'})) == None: 
        intro, ingredients, directions, meta = GetRecipe_old(soup)

    elif TryFind(soup.find('div',{'class':'hrecipe jetpack-recipe'})) != None: 
        intro, ingredients, directions, meta = GetRecipe_new(soup)

    return intro, ingredients, directions, meta


# In[319]:

def GetRecipeInfo_SK(soup):
    
    title = TryFind(soup.find('h1',{'class':'entry-title'}).find('a').contents[0])
    url = TryFind(soup.find('h1',{'class':'entry-title'}).find('a').attrs['href'])
    article_id = TryFind(soup.find('article').attrs['id'])
    published = TryFind(soup.find('time',{'class':'entry-date published'}).attrs['datetime'])
    updated = TryFind(soup.find('time',{'class':'updated'}).attrs['datetime'])
    author = TryFind(soup.find('span',{'class':'author vcard'}).find('a').contents[0])
    author_url = TryFind(soup.find('span',{'class':'author vcard'}).find('a').attrs['href'])
    
    recipe_text = GetEntryDescription(soup)
    
    recipe_intro, recipe_ingredients, recipe_directions, recipe_meta = GetIngredientsDirections(soup)


# In[192]:

def GetComments_SK(soup):
    commentlist = []
    for elem in soup.findAll('article',{'class':'comment-body'}):
        if elem.find('a').contents[0] != '\n':
            username = elem.find('a').contents[0]
            usersite = elem.find('a').attrs['href']

        else:
            username = 'anon'
            usersite = 'anon'
        
        usercomment = elem.find('div',{'class':'comment-content'}).find('p').get_text()
#         comment_timestamp = ''
#         comment
        

        commentlist.append((username, usersite, usercomment))
        
        return commentlist


# In[235]:




# In[317]:

a,b,c,d = GetRecipe_old(soup)
b


# ## get URLs

# In[5]:

urls_sk = URLFilter(ScrapeSitemap(sk_sitemap), sk_regex)


# In[60]:

soup = OpenPage(urls_sk[1])
soup1 = OpenPage(urls_sk[6])

soup.find('h1',{'class':'entry-title'}).find('a').contents[0], soup1.find('h1',{'class':'entry-title'}).find('a').contents[0]


# ### testing

# In[53]:

TryFind(soup.find('div',{'class':'hrecipe jetpack-recipe'})) == None


# In[193]:

GetComments_SK(soup)


# In[ ]:

def Title(soup):
    try: 
        recipename = soup.title  #.text.encode('ascii','ignore')
    except AttributeError as e:
        return None
    return recipename

def Ingredients(soup):
    try: 
        ingredients = soup.find('body').find('ul', {'class':'recipe-ingredients'}).findAll('span',{'class':'ingredient-name'})
    except AttributeError as e:
        return None
    return ingredients

def Description(soup):
    try: 
        description = soup.find('div',{'class':'entry-content'}).findAll('p')
    except AttributeError as e:
        return None

    return description

def Comments(soup):
    try:
        ratings = soup.findAll('div',{'class':'comment-content'}).text
    except AttributeError as e:
        return None
    return ratings

def Tips(soup):
    try:
        tips = soup.find('ul',{'class':'recipe-notes'}).text
    except AttributeError as e:
        return None
    return tips


# In[ ]:

def getEverything(page_number):
    soup = openPage(url+str(page_number))
    recipe_dict = {Title(soup) : {'url':url+str(page_number) ,'ingredients':Ingredients(soup), 'description':Description(soup), 'tips':Tips(soup), 'user_comments':Comments(soup)}}
    return recipe_dict


# In[ ]:




# In[ ]:

sk_list_cleaned = [elem.text.encode('ascii','ignore') for elem in sk_list]


# In[ ]:

sk_list_cleaned[0]


# In[ ]:

for elem in sk_list: 
    print(elem.text)


# In[ ]:



