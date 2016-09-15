
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
import datetime
import time

# %matplotlib inline

# sns.set_context('notebook')
# sns.set_style('ticks')


# ## general

# In[39]:

def OpenPage(url):
    try: 
        html = urlopen(url)
    except HTTPError: 
        return None

    try:
        pageData = BeautifulSoup(html, 'lxml') #,"html.parser")
    except AttributeError: 
        return None
    return pageData


def TryFind(search):
    try: 
        result = search
    except (AttributeError, TypeError): 
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


# ## SK-specific

# In[64]:

def GetEntryDescription_SK(soup):
    '''get the stuff thats an appendage to the actual recipe body (blog-y part)'''
    
    recipe_text = []
    for paragraph in TryFind(soup.select('div.smittenkitchen-print-hide > p')):
        expression = '.*(\s)*.*[Aa]go:.*'
        if paragraph.a:
            text = paragraph.get_text().strip()
            match = re.match(expression, text)
            if match: 
                continue
            else: recipe_text += [paragraph.get_text().strip()]
        
        else: recipe_text += [paragraph.get_text().strip()]
    return ''.join(recipe_text)


def GetRecipe_old(soup):
    '''get directions & ingredients separately'''
    
    intro, ingredients, directions, meta = [], [], [], []
    
    for item in TryFind(soup.select('div.entry-content > p')):
        if item.br:
#             line = TryFind(soup.find('div',{'class':'entry-content'}).findAll('p').findAll('br'))
            ingredients += [item.get_text().strip()]
        else: 
            directions += [item.get_text().strip()]
    recipe_servings = 'NA'
    recipe_time = 'NA'
    intro = 'NA'

    return intro, ingredients, ''.join(directions), recipe_servings, recipe_time 


def GetRecipe_new(soup):
    '''get directions & ingredients separately'''
    intro = []
    for item in TryFind(soup.findAll('div',{'class':'jetpack-recipe-notes'})):
        if item.a: 
            intro += item.get_text().strip()
        else: intro += item.get_text().strip()
    intro = ''.join(intro)
    
    ingredients = []    
    for item in TryFind(soup.findAll('li',{'class':'jetpack-recipe-ingredient'})):
        if item.a: 
            ingredients += [item.get_text().strip()]
        else: ingredients += [item.get_text().strip()]

            
    directions = []
    for item in TryFind(soup.find('div',{'class':'jetpack-recipe-directions'}).findAll('p')):
        if item.a: 
            directions += [item.get_text().strip()]
        else: directions += [item.get_text().strip()]

            
    recipe_meta = {}
    recipe_servings = TryFind(soup.find('li',{'class':'jetpack-recipe-servings'}).get_text())
    recipe_time = TryFind(soup.find('li',{'class':'jetpack-recipe-time'}).get_text())
            
    return ''.join(intro), ingredients, ''.join(directions), recipe_servings, recipe_time



def GetRecipeData_SK(soup):
    '''SK underwent a site redesign; find the right way to scrape the recipe data'''
    
    if TryFind(soup.find('div',{'class':'hrecipe jetpack-recipe'})) == None: 
        intro, ingredients, directions, recipe_servings, recipe_time = GetRecipe_old(soup)

    elif TryFind(soup.find('div',{'class':'hrecipe jetpack-recipe'})) != None: 
        intro, ingredients, directions, recipe_servings, recipe_time = GetRecipe_new(soup)

    return intro, ingredients, directions, recipe_servings, recipe_time



def CommentData_SK(comment, ID, children, child_id):
    '''get the data from each comment - '''
    comment_info = {}
    
    if comment.find('a').contents[0] != '\n':
        comment_info['username'] = comment.find('a').contents[0]
        comment_info['usersite'] = comment.find('a').attrs['href']

    else:
        comment_info['username'] = comment.find('b',{'class':'fn author-name'}).get_text().strip()
        comment_info['usersite'] = 'none'

    comment_info['usercomment'] = comment.find('div',{'class':'comment-content'}).find('p').get_text().strip()
    comment_info['children'] = children
    comment_info['child_id'] = child_id
    comment_info['commentID'] = ID

    return comment_info


# In[5]:

def GetComments_SK(soup):
    '''get comments and their place in the hierarchy'''

    comments_data = {}

    allcomments = TryFind(soup.find('ol',{'class':'comment-list'}))
    number_of_comments = len(allcomments.findAll('article',{'class':'comment-body'}))

    comment = allcomments.find('article',{'class':'comment-body'})

    for comment_ID in range(0, number_of_comments):

        nextComment = comment.findNext('article')

#         # look for parents
#         if comment_ID!= 1: 
#             if comment.parent.parent['class'][0] == 'children':
#                 comment_has_parent, parent_id = 'yes', 0
#         else: comment_has_parent, parent_id = 'no', 0


        # look for children
        if comment_ID< number_of_comments-1:
            if nextComment.parent.parent['class'][0] == 'children':
                comment_has_children, child_id = 'yes', comment_ID+1
            else: comment_has_children, child_id = 'no', 0 

        comments_data[comment_ID] = CommentData_SK(comment, comment_ID, comment_has_children, child_id)

        comment = comment.findNext('article')

    return comments_data, number_of_comments


# In[30]:

def GetRecipe_SK(soup, ID):
    '''get all the post data from a given url'''
    recipe = {}
    recipe_data = {}
    
    recipe_data['title'] = TryFind(TryFind(soup.find('h1',{'class':'entry-title'})).find('a').contents[0])    
    recipe_data['url'] = TryFind(TryFind(soup.find('h1',{'class':'entry-title'})).find('a').attrs['href'])
    recipe_data['article_id'] = TryFind(TryFind(soup.find('article')).attrs['id'])
    recipe_data['published'] = TryFind(soup.find('time')).attrs['datetime']
#                 TryFind(TryFind(soup.find('time',{'class':'entry-date published'})).attrs['datetime'])
    recipe_data['updated'] = TryFind(TryFind(soup.find('time',{'class':'updated'})).attrs['datetime'])
    recipe_data['author'] = TryFind(TryFind(soup.find('span',{'class':'author vcard'})).find('a').contents[0])
    recipe_data['author_url'] = TryFind(TryFind(soup.find('span',{'class':'author vcard'})).find('a').attrs['href'])
    
    recipe_data['introductory_text'] = GetEntryDescription_SK(soup)
    
    recipe_intro, recipe_ingredients, recipe_directions, recipe_servings, recipe_time = GetRecipeData_SK(soup)
    
    recipe_data['recipe_notes'] = recipe_intro
    recipe_data['ingredients'] = recipe_ingredients
    recipe_data['directions'] = recipe_directions
    recipe_data['servings'] = recipe_servings
    recipe_data['time'] = recipe_time
    
    recipe[ID] = recipe_data
    
    return recipe, recipe_data['title']


# ## set preliminaries

# ## get URLs

# In[7]:

url = 'https://smittenkitchen.com'
sk_sitemap = 'https://smittenkitchen.com/sitemap.xml'

# for SK, recipes are listed in <url>/yr/mo/<name> format, other aggregations/lists do not have this same formatting 
sk_regex = 'https://smittenkitchen.com/[0-9]{3,}.*'


urls_sk = URLFilter(ScrapeSitemap(sk_sitemap), sk_regex)


# # Scraper

# In[62]:

CommentsFrame = pd.DataFrame()
RecipeFrame = pd.DataFrame()

for recipenumber, url in enumerate(urls_sk): 
    soup = OpenPage(url)
    
    comments, commentnumber = GetComments_SK(soup)
    recipe, title = GetRecipe_SK(soup, recipenumber)


    CommentsFrame_temp = pd.DataFrame.from_dict(comments,orient='index')
    RecipeFrame_temp = pd.DataFrame.from_dict(recipe,orient='index')

    CommentsFrame_temp['recipeName'] = title
    CommentsFrame_temp['recipeID'] = recipenumber
    CommentsFrame_temp['recipeURL'] = url

    RecipeFrame_temp['numberofcomments'] = commentnumber


    CommentsFrame = pd.concat([CommentsFrame, CommentsFrame_temp], ignore_index=True)
    RecipeFrame = pd.concat([RecipeFrame, RecipeFrame_temp], ignore_index=True)   

    time.sleep(5)
    
CommentsFrame.to_csv('SmittenKitchen_Comments.csv')
RecipeFrame.to_csv('SmittenKitchen_Recipes.csv')


# ### testing

# In[ ]:



