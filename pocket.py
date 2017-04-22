#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @@@ kontroly
# ukazatel uploadu na Pocket
# zjednodušit logování záznamů - aby se pokaždé nemusela sjížděj celá funkce, tj. otevírat a zavírat db...

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
	return sortListOfDicts	(parsed_articles,ID,True)
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
	import time, logging, logging.config
	import os

	log_lvl = LOGGING_LEVELS[prs()]

	# logging
	log_debug_path = absFilePath('logs/logging_debug.log')
	log_info_path = absFilePath('logs/logging_info.log')
	logging_conf = absFilePath('logging.conf')
	logging.config.fileConfig(logging_conf,defaults={'debug_file': log_debug_path,'info_file':log_info_path})
	logger1 = logging.getLogger(__name__)
	logger1.setLevel(log_lvl)

	result_parsed_articles = []
	page_nr = 1
	batch_time_to_log = int(time.time())
	
	# create a local copy of a dropbox file
	dropbox_token = readTabbedFile(absFilePath(CREDENTIALS_DROPBOX_FL))[0]
	drop = Drop(dropbox_token)
	
	local_path = readTabbedFile(absFilePath(LOCAL_FILE_ADDRESS))
	# local file path defined in the parameter file
	if local_path:
		local_path = local_path[0]
		if os.path.isdir(local_path):
			local_path = os.path.join(local_path,DB_NM)
		else:
			# local file path = predifend file name stored in script directory
			local_path = None
	db_nm = drop.getTempFile(drop_fl_nm=DB_NM,local_fl_nm=local_path)
	
	SU.createTable(db_nm,TBL_NM,TBL_DEFINITION,1)
	latest_db_record = SU.readLatestRecord(db_nm,TBL_NM,ID,'desc')
	latest_db_id = latest_db_record[0] if latest_db_record else None
	logger1.debug('latest_db_id (latest recorded article ID): {}'.format(latest_db_id))
	logger1.debug('===============================================')
	
	while True:
		logger1.debug('PAGE # {}'.format(page_nr))
		articles_on_page = getArticles('{0}{1}'.format(URL,page_nr))
		articles_ids = [i[ID] for i in articles_on_page]
		logger1.debug('articles_ids (IDs of fetched articles TOTALLING {0}): {1}'.format(len(articles_ids),articles_ids))

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
				logger1.debug('articles_on_page_undone (IDs of articles fetched AND previously unprocessed, TOTALLING {0}): {1}'.format(len(articles_on_page_undone),[item[ID] for item in articles_on_page_undone]))
				logger1.debug('result_parsed_articles (so far, TOTALLING {0}): {1}'.format(len(result_parsed_articles),[item[ID] for item in result_parsed_articles]))		
				break
		else:
			result_parsed_articles.extend(articles_on_page)
			break
		result_parsed_articles.extend(articles_on_page)
		page_nr += 1
		logger1.debug('articles_on_page_undone (IDs of articles fetched AND previously unprocessed, TOTALLING {0}): {1}'.format(len(articles_on_page_undone),[item[ID] for item in articles_on_page_undone]))
		logger1.debug('result_parsed_articles (so far, TOTALLING {0}): {1}'.format(len(result_parsed_articles),[item[ID] for item in result_parsed_articles]))
		logger1.debug('-----------------------------------------------')

	logger1.debug('===============================================')
	logger1.debug('result_parsed_articles (TOTALLING): {0}'.format(len(result_parsed_articles)))
	logger1.debug('parsed articles IDs: {0}'.format([item[ID] for item in result_parsed_articles]))
	# log the new fetched articles into the db and save them to Pocket
	if result_parsed_articles != []:
		cons_key, access_tkn = readTabbedFile(absFilePath(CREDENTIALS_POCKET_FL))
		for art_to_log in result_parsed_articles:
			# @@@ 
			# art_to_log.extend(batch_time_to_log)
			try:
				SU.logRecord(db_nm,TBL_NM,*art_to_log.values(),batch_time_to_log) # dictionary turned into list of values

				logger1.debug('logged into db: {0}'.format(art_to_log))
			except Exception as e:
				logger1.info('=== EXCEPTION: {0} for article: {1}'.format(e,art_to_log))
		# upload the local copy of the file back to dropbox, delete the local file
		_upload_resp = drop.uploadTempFile()
		if not _upload_resp:
			logger1.debug('file not uploaded back to Dropbox!')
		for art_to_post in result_parsed_articles[::-1]:
			pocket_resp = addItemToPocket(cons_key,access_tkn,art_to_post[LINK])
			# @@@ kontrola?

		

