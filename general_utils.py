#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, argparse

def prs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--log_level', type=str, default='info',
                        help='The desired logging level.')
    args = parser.parse_args()
    # returns a () of arguments
    return args.log_level

def absFilePath(rel_path):
	"""
	constructs absolute path based on relative path and the script directory
	"""
	script_dir = os.path.dirname(__file__)
	return os.path.join(script_dir, rel_path)

def readTabbedFile(file_nm):
	"""
	read and parse a text file
	return a list of [login name, password]
	"""
	tabbed_list = []
	try:
		with open(file_nm,'r') as f:
			content_split = f.read().split()
			for i in content_split:
				tabbed_list.append(i.strip())		
		# return [content_split[0].strip(),content_split[1].strip()]
		return tabbed_list
	# except FileNotFoundError:
	# 	return []
	except Exception as e:
		raise Exception(e)

def sortListOfDicts(lst_of_dicts,key,rev=False):
	"""
	using the Perl Schwarzian transform, the list is sorted based on the selected dictionary key
	optional reverse order
	"""
	sort_on = key
	decorated_lst = [(dict_[sort_on], dict_) for dict_ in lst_of_dicts]
	decorated_lst.sort(reverse=rev)
	return [dict_ for (key, dict_) in decorated_lst]
