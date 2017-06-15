#!/usr/bin/env python3
# -*- coding: utf-8 -*-

DB_NM = 'ars_articles.db'
TBL_NM = 'articles'

ID = 'id'
LINK = 'link'
TITLE = 'title'
AUTHOR = 'author'
DTTIME = 'dttime'
DTTIME_LOG = 'dttime_log'

TBL_DEFINITION = '{0} INTEGER, {1} TEXT, {2} TEXT, {3} TEXT, {4} INTEGER, {5} INTEGER'.format(ID,LINK,TITLE,AUTHOR,DTTIME,DTTIME_LOG)

URL = 'https://arstechnica.com/page/'

LOCAL_FILE_ADDRESS = 'local_file_address.txt'
CREDENTIALS_POCKET_FL = 'pocket_creds.txt'
CREDENTIALS_DROPBOX_FL = 'dropbox_creds.txt'
# REDIRECT_URI = 'http://arstechnica.com'
DEBUG_LOG = 'debug.log'

LOGGING_LEVELS = {'debug':10,'info':20,'warning':30,'error':40,'critical':50}