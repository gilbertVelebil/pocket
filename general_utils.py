#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @@@ Drop.getTempFile a Drop.uploadTempFile - dodelat akce pro except Exception

import os, argparse
import dropbox

def prs():
    parser = argparse.ArgumentParser()
    parser.add_argument('--log_level', type=str, default='info',
                        help='The desired logging level.')
    args = parser.parse_args()
    # returns a () of arguments
    return args.log_level


# class Drop(dropbox.client.DropboxClient):
class Drop(dropbox.Dropbox):

	def __init__(self,token:str):
		"""
		Args:
			param1: Dropbox token
	    
	    Return:
	    	Dropbox object
	    """
		super().__init__(token)
		import os
		self.drop_fl_nm = None
		self.local_file_abs_path = None

	def getTempFile(self,drop_fl_nm:str,local_fl_nm:str=None):
		"""
		Args:
			(param1: Dropbox object)
			param2: Dropbox file name (str)
			param3: local file name (str), if not supplied, Dropbox file name is used
	    
	    Return:
	    	the name of the local file into which the content of the Dropbox file was dumped(as string)
	    """

		self.drop_fl_nm = drop_fl_nm
		if local_fl_nm:
				# a) relative local file name supplied
				if local_fl_nm[0] == '/':
					self.local_file_abs_path = local_fl_nm
				# b) absolute local file name supplied
				else:
					self.local_file_abs_path = absFilePath(local_fl_nm)
		# c) none supplied
		else:
			self.local_file_abs_path = absFilePath(drop_fl_nm)

		# XXX
		# self.local_file_abs_path = absFilePath(local_fl_nm) if local_fl_nm else absFilePath(drop_fl_nm)
		# self.resp = self.get_file('/{}'.format(self.drop_fl_nm))
		try:
			self.files_download_to_file(self.local_file_abs_path,'/{}'.format(self.drop_fl_nm))
		except ApiError:
			return False

		# XXX
		# self.drop_file_content = self.resp.read()
		# self.local_fl = open(self.local_file_abs_path,'wb')
		# self.local_fl.write(self.drop_file_content)
		# self.local_fl.close()
		
		return self.local_file_abs_path
		
		# XXX
		# self.local_fl = open(self.local_file_abs_path,'rb')
		# return self.local_fl

	def uploadTempFile(self,drop_fl_nm:str=None,local_fl_nm:str=None,del_local=True):
		"""
		Args:
			(param1: Dropbox object)
			param2: Dropbox file name (str), if not supplied, getself. is used
			param3: local file name (str), if not supplied, self. is used
	    	param3: bool delete local file, def. True
	    Return:
	    	Dropbox put_file response
	    	if local file name/Dropbox file name not supplied and has not been created by getTemplateFile,
	    	return False
	    """
	    	    
	    # XXX
	    # local file name
		# if local_fl_nm:
		# 	self.local_file_abs_path = absFilePath(local_fl_nm)
		# elif not self.local_file_abs_path:
		# 	return False


		# local file name supplied
		if local_fl_nm:
				# a) relative local file name supplied
				if local_fl_nm[0] == '/':
					self.local_file_abs_path = local_fl_nm
				# b) absolute local file name supplied
				else:
					self.local_file_abs_path = absFilePath(local_fl_nm)
		# c) none supplied >> self.local_file_abs_path is used, else return False
		elif not self.local_file_abs_path:
			return False

		# dropbox file name
		# supplied
		if drop_fl_nm:
			self.drop_fl_nm = drop_fl_nm
		# self.drop_fl_nm used or else, derived from local file name
		elif not self.drop_fl_nm:
			self.drop_fl_nm = os.path.basename(self.local_file_abs_path)
		
		# XXX
		# self.local_fl = open(self.local_file_abs_path,'rb')
		# resp = self.put_file('/{}'.format(self.drop_fl_nm),self.local_fl,overwrite=True)
		# self.local_fl.close()
		try:
			with open(self.local_file_abs_path,'rb') as _local_fl:
				resp = self.files_upload(_local_fl.read(), '/{}'.format(self.drop_fl_nm), mode=dropbox.files.WriteMode('overwrite'))
			if del_local:
				os.remove(self.local_file_abs_path)
		except Exception:
			return False

		# @@@ alternative: True
		return resp


# drop_file = client.get_file('/ars_articles.db')

# put_file('/ars_articles.db',fl,overwrite=True)
 
# drop_file_cont = drop_file.read()
# temp_file = tempfile.NamedTemporaryFile()
# temp_file.write(drop_file_cont)

# con = sqlite3.connect(temp_file.name)
# cur = con.cursor()
# resp = cur.execute('SELECT dttime_log, COUNT(*) FROM articles GROUP BY 1')
		

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
