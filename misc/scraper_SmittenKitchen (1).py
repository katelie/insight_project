
# coding: utf-8

# In[73]:

from IPython.core.display import HTML
HTML("<style>.container { width:100% !important; float:left}</style>")


# In[74]:

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
import datetime
import time

# %matplotlib inline

# sns.set_context('notebook')
# sns.set_style('ticks')


# In[110]:

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


def TryFind(search):
    try: 
        result = search
    except AttributeError as e: 
        return None
    return result


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


def GetEntryDescription(soup):
    '''get the stuff thats an appendage to the actual recipe body (blog-y part)'''
    
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


def GetRecipe_old(soup):
    '''get directions & ingredients separately'''
    
    intro, ingredients, directions, meta = [], [], [], []
    
    for item in TryFind(soup.select('div.entry-content > p')):
        if item.br:
            line = TryFind(soup.find('div',{'class':'entry-content'}).findAll('p').findAll('br'))
            
            ingredients += [item.get_text().strip()]
        else: 
            directions += [item.get_text().strip()]
    meta += ['NA']
    intro += ['NA']

    return intro, ingredients, directions, meta


def GetRecipe_new(soup):
    '''get directions & ingredients separately'''
    intro = []
    for item in TryFind(soup1.findAll('div',{'class':'jetpack-recipe-notes'})):
        if item.a: 
            intro += item.get_text().strip()
        else: intro += item.get_text().strip()
    intro = ''.join(intro)
    
    ingredients = []    
    for item in TryFind(soup1.findAll('li',{'class':'jetpack-recipe-ingredient'})):
        if item.a: 
            ingredients += [item.get_text().strip()]
        else: ingredients += [item.get_text().strip()]

            
    directions = []
    for item in TryFind(soup1.find('div',{'class':'jetpack-recipe-directions'}).findAll('p')):
        if item.a: 
            directions += [item.get_text().strip()]
        else: directions += [item.get_text().strip()]

            
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


# In[127]:

def GetCommentData_SK(soup):
    commentlist = []
    for elem in soup.findAll('article',{'class':'comment-body'}):
        if elem.find('a').contents[0] != '\n':
            username = elem.find('a').contents[0]
            usersite = elem.find('a').attrs['href']

        else:
            username = elem.find('b',{'class':'fn author-name'}).get_text().strip()
            usersite = 'nosite'
        
        usercomment = elem.find('div',{'class':'comment-content'}).find('p').get_text()

        
        
#         commentlist.append((username, usersite, usercomment))
        
        return commentlist


# ## set preliminaries

# In[75]:

url = 'https://smittenkitchen.com'
sk_sitemap = 'https://smittenkitchen.com/sitemap.xml'

# for SK, recipes are listed in <url>/yr/mo/<name> format, other aggregations/lists do not have this same formatting 
sk_regex = 'https://smittenkitchen.com/[0-9]{3,}.*'


# ## get URLs

# In[ ]:

urls_sk = URLFilter(ScrapeSitemap(sk_sitemap), sk_regex)


# In[ ]:

soup = OpenPage(urls_sk[0])
soup1 = OpenPage(urls_sk[5])

soup.find('h1',{'class':'entry-title'}).find('a').contents[0], soup1.find('h1',{'class':'entry-title'}).find('a').contents[0]


# In[125]:

def GetRecipeInfo_SK(soup):
    '''get all the post data from a given url'''
    
    recipe_data = {}
    
    recipe_data['title'] = TryFind(soup.find('h1',{'class':'entry-title'}).find('a').contents[0])    
    recipe_data['url'] = TryFind(soup.find('h1',{'class':'entry-title'}).find('a').attrs['href'])
    recipe_data['article_id'] = TryFind(soup.find('article').attrs['id'])
    recipe_data['published'] = TryFind(soup.find('time',{'class':'entry-date published'}).attrs['datetime'])
    recipe_data['updated'] = TryFind(soup.find('time',{'class':'updated'}).attrs['datetime'])
    recipe_data['author'] = TryFind(soup.find('span',{'class':'author vcard'}).find('a').contents[0])
    recipe_data['author_url'] = TryFind(soup.find('span',{'class':'author vcard'}).find('a').attrs['href'])
    
    recipe_data['recipe_text'] = GetEntryDescription(soup)
    
    recipe_intro, recipe_ingredients, recipe_directions, recipe_meta = GetRecipe(soup)
    
    recipe_data['recipe_intro'] = recipe_intro
    recipe_data['recip_ingredients'] = recipe_ingredients
    recipe_data['recip_directions'] = recipe_directions
    recipe_data['recip_meta'] = recipe_meta
    
    
    return recipe_data
    


# In[161]:

def CommentData_SK(comment, children, child_id):
    comment_data = {}
    
    for elem in soup.findAll('article',{'class':'comment-body'}):
        if elem.find('a').contents[0] != '\n':
            comment_data['username'] = elem.find('a').contents[0]
            comment_data['usersite'] = elem.find('a').attrs['href']

        else:
            comment_data['username'] = elem.find('b',{'class':'fn author-name'}).get_text().strip()
            comment_data['usersite'] = 'nosite'
        
        comment_data['usercomment'] = elem.find('div',{'class':'comment-content'}).find('p').get_text()
        comment_data['children'] = children
        comment_data['child_id'] = child_id
        comment_data['parent_id'] = parent_id
        
        return comment_data

def GetComments(soup):

    # Get comments with heirarchy info 
    comments = {}

    allcomments = TryFind(soup.find('ol',{'class':'comment-list'}))
    number_of_comments = len(allcomments.findAll('article',{'class':'comment-body'}))

    comment = allcomments.find('article',{'class':'comment-body'})

    for i in range(0, number_of_comments):

        nextComment = comment.findNext('article')

        # look for parents
        if i != 1: 
            if comment.parent.parent['class'][0] == 'children':
                comment_has_parent, parent_id = 'yes', 0
        else: comment_has_parent, parent_id = 'no', 0


        # look for children
        if i < number_of_comments-1:
            if nextComment.parent.parent['class'][0] == 'children':
                comment_has_children, child_id = 'yes', i+1
            else: comment_has_children, child_id = 'no', 0 

        comments[str(i)] = CommentData_SK(comment, comment_has_children, child_id)

        comment = nextComment
        i += 1 

    return comments


# # Scraper

# In[ ]:




# ### testing

# In[160]:

len(comments)


# In[140]:

allcomments = soup.find('ol',{'class':'comment-list'})
comment = allcomments.find('article',{'class':'comment-body'})
nextComment = comment.findNext('article')
nextComment.parent.parent['class'][0]


# In[101]:

len(allcomments.findAll('article',{'class':'comment-body'}))


# In[ ]:

for elem in soup.findAll('article',{'class':'comment-body'}):
    print(elem.parent.parent.name)
    print(soup.find('ol').parent.parent)


# In[ ]:

a.findAll('div',{'class':'comment-content'})


# In[ ]:

a.find('div',{'class':'comment-content'}).get_text().strip()


# In[ ]:




# In[ ]:



other things to get: 
# of comments

# In[ ]:

len(urls_sk)


# In[ ]:




# In[ ]:

TryFind(soup.find('div',{'class':'hrecipe jetpack-recipe'})) == None


# In[ ]:

GetComments_SK(soup)


# In[ ]:

intro, ingredients, directions, meta = [], [], [], []

for item in TryFind(soup.select('div.entry-content > p')):
    if item.br:
#         line = TryFind(soup.find('div',{'class':'entry-content'}).findAll('p').findAll('br'))

        ingredients += [item.get_text()]
    else: 
        directions += [item.get_text()]
meta += ['NA']
intro += ['NA']



# In[ ]:

a = TryFind(soup.select('div.entry-content > p'))
a[1].br
new = a.nextSibling
new

for br in soup.findAll('br'):
    next = br.nextSibling
    if not (next and isinstance(next,NavigableString)):
        continue
    next2 = next.nextSibling
    if next2 and isinstance(next2,Tag) and next2.name == 'br':
        text = str(next).strip()
        if text:
            print "Found:", next
# In[ ]:



