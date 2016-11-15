#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import urllib
from collections import OrderedDict
from pocketAPI import Pocket

from general_utils import *
from shared_constants import *

# příprava (doladit potvrzování pomocí redirect url)
# p = Pocket(CONSUMER_KEY,REDIRECT_URI)
# code = p.get_request_token()
# redirect_url = p.get_authorize_url(code) # go to the address, confirm authorization
# access_tkn = p.get_access_token(code)

###########################################################################################################################
# původní ruční kód, nefunguje získání access_tokenu, processingotože nebyla potvrzena autorizace
# get_code_args = {'consumer_key':CONSUMER_KEY,'redirect_uri':REDIRECT_URI}
# r = requests.post('https://getpocket.com/v3/oauth/request',data=get_code_args)#,headers=POCKET_HEADERS)
# raw_code = r.text
# code  = raw_code[raw_code.find('=')+1:]

# get_access_token  = {'consumer_key':CONSUMER_KEY,'code':code}

# # url_addr = 'https://getpocket.com/auth/authorize?request_token={0}&redirect_uri={1}'.format(code,REDIRECT_URI)
# # html = urllib.request.urlopen(url_addr)

# r = requests.post('https://getpocket.com/v3/oauth/authorize',data=get_access_token)#,headers=POCKET_HEADERS)
# raw_access_token = r.text
# access_token = raw_access_token[raw_access_token.find('=')+1:]
###########################################################################################################################


# adding items to Pocket
def addItemToPocket(cons_key,access_tkn,item_url):
	pock = Pocket(cons_key)
	pock.set_access_token(access_tkn)
	resp = pock.add(url=item_url)
	return resp


# webscraping
def getArticles(url_addr:str):
	from bs4 import SoupStrainer as  SS, BeautifulSoup as BS
	import operator
	import urllib.request
	html = urllib.request.urlopen(url_addr)
	articles = BS(html,'html.parser',parse_only=SS('article'))
	parsed_articles = []
	for i in articles:
		parsed_articles.append(parseArticle(i))
	return sortListOfDicts(parsed_articles,ID,True)
	# return parsed_articles.sort(key=operator.itemgetter(ID),reverse=True)

# specifically for arstechnica.com!
def parseArticle(art):
	res = OrderedDict()
	res['id'] = int(art['data-post-id'])
	res['link'] = art.header.a['href']
	res['title'] = art.header.a.text
	res['author'] = art.find_all(itemprop='name')[0].text
	res['dttime'] = int(art.find_all(bs_tag_has_attr_datatime)[0]['data-time'])
	return res

# BeautifulSoup aux funciton
def bs_tag_has_attr_datatime(tag):
	return tag.has_attr('data-time')



if __name__ == '__main__':
	
	import sqlite_utils as SU
	import time

	result_parsed_articles = []
	page_nr = 1
	batch_time_to_log = int(time.time())
	SU.createTable(DB_NM,TBL_NM,TBL_DEFINITION,1)

	while True:
		latest_db_record = SU.readLatestRecord(DB_NM,TBL_NM,ID,'desc')
		latest_db_id = latest_db_record[0] if latest_db_record else None
		articles_on_page = getArticles('{0}{1}'.format(URL,page_nr))
		articles_ids = [i[ID] for i in articles_on_page]

		# if #1: is there anything in the database or are we processing one Ars Technica page only?
		if latest_db_id != None:
			articles_on_page_undone = []
			try:
				latest_db_id_in_articles = articles_ids.index(latest_db_id)
			except ValueError as E:
				latest_db_id_in_articles = None
			# if #2: was the latest db-logged id (ie. article) found in the fetched articles?
			if latest_db_id_in_articles != None:
				articles_on_page_undone = articles_on_page [:latest_db_id_in_articles] # scapes the records past the latest logged id (ie. records already processed)
				result_parsed_articles.extend(articles_on_page_undone)
				break
		else:
			result_parsed_articles.extend(articles_on_page)
			break
		page_nr += 1

	# log the new fetched articles into the db and save them to Pocket
	if result_parsed_articles != []:
		cons_key, access_tkn = readTabbedFile(readTabbedFile(CREDENTIALS_FL))
		for art_to_log in result_parsed_articles:
			# @@@ 
			# art_to_log.extend(batch_time_to_log)
			SU.logRecord(DB_NM,TBL_NM,*art_to_log.values(),batch_time_to_log) # dictionary turned into list of values
		for art_to_post in result_parsed_articles[::-1]:
			pocket_resp = addItemToPocket(cons_key,access_tkn,art_to_post[LINK])

		

