
# coding: utf-8

# In[12]:

from IPython.core.display import HTML
HTML("<style>.container { width:100% !important; float:center}</style>")


# In[13]:

from __future__ import division, print_function

# from sys import argv
# import os
# import glob
# import math
import re
import pandas as pd
# import numpy as np
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
from urllib2 import HTTPError
from bs4 import BeautifulSoup
import datetime
import time

# %matplotlib inline

# sns.set_context('notebook')
# sns.set_style('ticks')


# ## general

# In[14]:

def OpenPage(url):
    try: 
        html = urlopen(url)
    except HTTPError as e: 
        return None

    try:
        pageData = BeautifulSoup(html,"html.parser")  #, 'lxml') #
    except AttributeError as e: 
        return None
    return pageData


def TryFind(search):
    try: 
        result = search
    except AttributeError as e: 
        return None
    if result == None: 
        return None
    return result


def GetText(search):
    if search == None:
        return None
    else: 
        try: 
            text = search.get_text().strip()
        except AttributeError as e: 
            return None
        if text == None: 
            return None
        return text
    
    
def GetAttribute(search, attribute):
    if search == None:
        return None
    else:
        try: 
            attr = search.attrs[attribute]
        except AttributeError as e:
            return None
        if attr == None: 
            return None
        
        return attr


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

# In[15]:

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
            else: recipe_text += [GetText(paragraph)]
        
        else: recipe_text += [GetText(paragraph)]
    return ''.join(recipe_text)


def GetRecipe_old(soup):
    '''get directions & ingredients separately'''
    
    intro, ingredients, directions, meta = [], [], [], []
    
    for item in TryFind(soup.select('div.entry-content > p')):
        if item.br:
            ingredients += [GetText(item)]
        else: 
            directions += [GetText(item)]
    recipe_servings = 'NA'
    recipe_time = 'NA'
    intro = 'NA'

    return intro, ingredients, ''.join(directions), recipe_servings, recipe_time 


def GetRecipe_new(soup):
    '''get directions & ingredients separately'''
    intro = []
    for item in TryFind(soup.findAll('div',{'class':'jetpack-recipe-notes'})):
        if item.a: 
            intro += GetText(item)
        else: intro += GetText(item)
    intro = ''.join(intro)
    
    ingredients = []    
    for item in TryFind(soup.findAll('li',{'class':'jetpack-recipe-ingredient'})):
        ingredients += [GetText(item)]
#         if item.a: 
#             ingredients += [GetText(item)]
#         else: ingredients += [GetText(item)]

            
    directions = []
    for item in TryFind(soup.find('div',{'class':'jetpack-recipe-directions'}).findAll('p')):
        if item == None: 
            directions += 'none'
#         elif item.a: 
#             directions += [GetText(item)]
        else: 
            directions += [GetText(item)]

    recipe_servings = GetText(TryFind(soup.find('li',{'class':'jetpack-recipe-servings'})))
    recipe_time = GetText(TryFind(soup.find('li',{'class':'jetpack-recipe-time'})))
            
    return ''.join(intro), ingredients, ''.join(directions), recipe_servings, recipe_time



def GetRecipeData_SK(soup):
    '''SK underwent a site redesign; find the right way to scrape the recipe data'''
    
    if TryFind(soup.find('div',{'class':'hrecipe jetpack-recipe'})) == None: 
#         print('old')
        intro, ingredients, directions, recipe_servings, recipe_time = GetRecipe_old(soup)

    elif (TryFind(soup.find('div',{'class':'hrecipe jetpack-recipe'})) != None): 
        if (TryFind(soup.find('div',{'class':'hrecipe jetpack-recipe-notes'})) != None) & (TryFind(soup.find('div',{'class':'hrecipe jetpack-recipe-ingredient'})) != None) & (TryFind(soup.find('div',{'class':'hrecipe jetpack-recipe-directions'})) != None): 
#         print('new')
            intro, ingredients, directions, recipe_servings, recipe_time = GetRecipe_new(soup)
        
        else: 
            intro, ingredients, directions, recipe_servings, recipe_time = GetRecipe_old(soup)
    else: 
        intro, ingredients, directions, recipe_servings, recipe_time = GetRecipe_old(soup)

    return intro, ingredients, directions, recipe_servings, recipe_time


# In[16]:

def GetCommentData_SK(comment, ID, children, child_id):
    '''get the data from each comment - '''
    comment_info = {}

    name = TryFind(comment.find('b',{'class':'fn author-name'}))
    if TryFind(name.find('a')) == None:
        comment_info['username'] = GetText(TryFind(comment.find('b',{'class':'fn author-name'})))
        comment_info['usersite'] = 'none'

    else: 
        comment_info['username'] = TryFind(comment.find('a')).contents[0]
        comment_info['usersite'] = TryFind(comment.find('a')).attrs['href']

        
    comment_info['usercomment'] = GetText(TryFind(comment.find('div',{'class':'comment-content'}).find('p')))
    comment_info['children'] = children
    comment_info['child_id'] = child_id
    comment_info['commentID'] = ID
    
    comment_info['comment_time'] = GetKeys(soup.find('time',{'class':'comment-time'}))[1][:19]
                            # datetime.datetime.strptime(time, '%Y-%m-%dt%H:%M:%S').strftime()

    return comment_info


def GetKeys(search):
    try: 
        results = TryFind(search).attrs
    except AttributeError as e:
        return None
    
    if results == None: 
        return '0000-00-00t00:00:00'
    
    return results.keys()


# In[17]:

def GetComments_SK(soup):
    '''get comments and their place in the hierarchy'''

    comments_data = {}
    comment_has_children, child_id = 'no', 0 

    allcomments = TryFind(soup.find('ol',{'class':'comment-list'}))
    number_of_comments = len(soup.findAll('article',{'class':'comment-body'}))

    comment = TryFind(allcomments.find('article',{'class':'comment-body'}))

    for comment_ID in range(0, number_of_comments):

        nextComment = comment.findNext('article',{'class':'comment-body'})

        if comment_ID < number_of_comments-1:
            if nextComment.parent.parent['class'][0] == 'children':
                comment_has_children, child_id = 'yes', comment_ID+1
            else: comment_has_children, child_id = 'no', 0 
        else: comment_has_children, child_id = 'no', 0 
            

        comments_data[comment_ID] = GetCommentData_SK(comment, comment_ID, comment_has_children, child_id)

        comment = comment.findNext('article')

    return comments_data, number_of_comments


# In[18]:

def GetRecipe_SK(soup, ID):
    '''get all the post data from a given url'''
    recipe = {}
    recipe_data = {}
    
    recipe_data['title'] = TryFind(TryFind(soup.find('h1',{'class':'entry-title'})).find('a').contents[0])    
    recipe_data['url'] = GetAttribute(TryFind(soup.find('h1',{'class':'entry-title'})).find('a'), 'href')
    recipe_data['article_id'] = TryFind(TryFind(soup.find('article')).attrs['id'])
    recipe_data['published'] = TryFind(soup.find('time')).attrs['datetime']
    recipe_data['updated'] = TryFind(TryFind(soup.find('time',{'class':'updated'})).attrs['datetime'])
    recipe_data['author'] = TryFind(TryFind(soup.find('span',{'class':'author vcard'})).find('a').contents[0])
    recipe_data['author_url'] = GetAttribute(TryFind(soup.find('span',{'class':'author vcard'})).find('a'), 'href')
    
    recipe_data['introductory_text'] = GetEntryDescription_SK(soup)
    
    recipe_intro, recipe_ingredients, recipe_directions, recipe_servings, recipe_time = GetRecipeData_SK(soup)
    
    recipe_data['recipe_notes'] = recipe_intro
    recipe_data['ingredients'] = recipe_ingredients
    recipe_data['directions'] = recipe_directions
    recipe_data['servings'] = recipe_servings
    recipe_data['time'] = recipe_time
    
    recipe_data['firstimageURL'] = GetAttribute(soup.find('img'), 'src')
    
    recipe[ID] = recipe_data
    
    return recipe, recipe_data['title']


# ## set preliminaries

# ## get URLs

# In[19]:

url = 'https://smittenkitchen.com'
sk_sitemap = 'https://smittenkitchen.com/sitemap.xml'

# for SK, recipes are listed in <url>/yr/mo/<name> format, other aggregations/lists do not have this same formatting 
sk_regex = 'https://smittenkitchen.com/[0-9]{3,}.*'


urls_sk = URLFilter(ScrapeSitemap(sk_sitemap), sk_regex)


# In[20]:

len(urls_sk), urls_sk[0]


# # Scraper

# In[21]:

# CommentsFrame = pd.DataFrame()
# RecipeFrame = pd.DataFrame()

for recipenumber, url in enumerate(urls_sk[1]): 
    print(len(urls_sk)-recipenumber)
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

    time.sleep(2)
    
CommentsFrame.to_csv('SmittenKitchen_Comments.csv', sep=',', encoding='utf-8')
RecipeFrame.to_csv('SmittenKitchen_Recipes.csv', sep=',', encoding='utf-8')

CommentsFrame.to_csv('SmittenKitchen_Comments.csv', sep=',', encoding='utf-8')
RecipeFrame.to_csv('SmittenKitchen_Recipes.csv', sep=',', encoding='utf-8')
# ### testing
GetComments_SK(soup)
comments_data = {}
comment_has_children, child_id = 'no', 0 

allcomments = TryFind(soup.find('ol',{'class':'comment-list'}))
number_of_comments = len(soup.findAll('article',{'class':'comment-body'}))

comment = TryFind(allcomments.find('article',{'class':'comment-body'}))

for comment_ID in range(0, number_of_comments):

    nextComment = comment.findNext('article',{'class':'comment-body'})
print(comment, nextComment)
# print(comment.parent.parent, nextComment.parent.parent)
#     if comment_ID < number_of_comments-1:
#         if nextComment.parent.parent
        
#         if nextComment.parent.parent['class'][0] == 'children':
#             comment_has_children, child_id = 'yes', comment_ID+1
#         else: comment_has_children, child_id = 'no', 0 
#     else: comment_has_children, child_id = 'no', 0 


#     comments_data[comment_ID] = GetCommentData_SK(comment, comment_ID, comment_has_children, child_id)

#     comment = comment.findNext('article')

GetAttribute((TryFind(nextComment.parent.parent)),'class')allcomments
nc.parent.parent    allcomments = TryFind(soup.find('ol',{'class':'comment-list'}))
    number_of_comments = allcomments.findAll('article',{'class':'comment-body'})
    number_of_comments
#     allcomments
#     allcomments.findAll('article',{'class':'comment-body'})# a = soup.find('article',{'class':'comment-body'})
a = a.findNext('article',{'class':'comment-body'})
aCommentsFrame.iloc[-1,:]datetime.datetime.strptime(time, '%Y-%m-%dt%H:%M:%S').strftime()