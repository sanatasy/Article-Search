# -*- coding: utf-8 -*-
"""
Created on Sat Oct 27 09:03:36 2018

@author: Sanata
"""

from nytimesarticle import articleAPI
import time 

article_search_key = "f5c106ba972147589d5534170d078b0b"

api = articleAPI(article_search_key )


articles = api.search( q = "science", 
                      fq = {"news_desk":"Science", 'source':['Reuters','AP', 'The New York Times'], 
                            'type':'News'}, 
                      begin_date = "20170101", 
                      end_date = "20171231")


def parse_articles(articles):
    '''
    This function takes in a response to the NYT api and parses
    the articles into a list of dictionaries
    '''
    news = []
    for i in articles['response']['docs']:
        dic = {}
        dic['id'] = i['_id']
        dic['headline'] = i['headline']['main'].encode("utf8")
        dic['date'] = i['pub_date'][0:10] # cutting time of day.
        #dic['section'] = i['section_name']
        dic['source'] = i['source']
        dic['type'] = i['type_of_material']
        dic['url'] = i['web_url']
        # locations
        locations = []
        for x in range(0,len(i['keywords'])):
            if 'glocations' in i['keywords'][x]['name']:
                locations.append(i['keywords'][x]['value'])
        dic['locations'] = locations
        # subject
        subjects = []
        for x in range(0,len(i['keywords'])):
            if 'subject' in i['keywords'][x]['name']:
                subjects.append(i['keywords'][x]['value'])
        dic['subjects'] = subjects  
        #organizations 
        organizations = []
        for x in range(0,len(i['keywords'])):
            if 'organizations' in i['keywords'][x]['name']:
                organizations.append(i['keywords'][x]['value'])
        dic['organizations'] = organizations
        news.append(dic)
    return(news) 


test = parse_articles(articles)


def get_articles(date,query):
    '''
    This function accepts a year in string format (e.g.'1980')
    and a query (e.g.'Amnesty International') and it will 
    return a list of parsed articles (in dictionaries)
    for that year.
    '''
    all_articles = []
    for i in range(0,100): #NYT limits pager to first 100 pages. But rarely will you find over 100 pages of results anyway.
        articles = api.search( q = query, 
                      fq = {"news_desk":"Science", 'source':['Reuters','AP', 'The New York Times']}, 
                      begin_date = date + '0101', 
                      end_date = date + '1231', 
                      page=i)
        print(i)
        time.sleep(2)
        articles = parse_articles(articles)
        all_articles.append(articles)
    return(all_articles)

all_articles = get_articles("2017","science")

saved = all_articles



import csv
keys = all_articles[0][0].keys()
with open('science-mentions.csv', 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    for i in range(0, 100):
        dict_writer.writerows(all_articles[i])


import pandas
import matplotlib.pyplot as plt

df = pandas.read_csv('science-mentions.csv')
df['date2'] = pandas.to_datetime(df['date'])
df['datemonth'] = df['date2'].dt.month

df = df.sort_values(by='datemonth', ascending=True)

group_by_month = df.groupby(['datemonth'])

counts = group_by_month.size()
counts.plot(kind = 'barh', stacked=True)
plt.title("Monthly NYT Science Articles in 2017")
plt.ylabel('Month')
plt.xlabel('Number of Articles')

plt.savefig('nyt_monthly.png')

#find journals 

df['organizations'].head()

journ = df[df['organizations'].str.contains('Journal')]
journals = journ['organizations'].tolist()

import ast
x = ast.literal_eval(journ['organizations'][475])

idx = journ['organizations'].index

jlist =[]
for x in idx:
    words = ast.literal_eval(journ['organizations'][x])
    jlist.append(words)
    

jlist = sum(jlist, [])
journals = [s for s in jlist if "Journal" in s]

for i, v in enumerate(journals) :
    journals[i] = v.replace("(Journal)","")


jdf = pandas.DataFrame()
jdf['journalName'] = journals

jdf.to_csv('nyt_journals.csv')

