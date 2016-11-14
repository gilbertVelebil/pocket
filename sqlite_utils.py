import os
import sqlite3
import sqlobject.sqlbuilder as SOB

def createTable(db:str,tbl_nm:str,tbl_definition,index_col:int=None)->bool:
	"""
	create a table (if it does not exist) in the given db based on the given definition
	optional: index column
	return: True (tbl created), False (tbl already existed)
	"""
	try:
		ret = False
		if os.path.isfile(db):
			con = sqlite3.connect(db)
			cur = con.cursor()
			cur.execute("PRAGMA table_info({0})".format(tbl_nm))

			if cur.fetchall() == []:
				cur.execute("CREATE TABLE {0} ({1});".format(tbl_nm,tbl_definition))
				if index_col and index_col > 0:
					cur.execute("SELECT * FROM {0} LIMIT 1".format(tbl_nm))
					col_nms = [description[0] for description in cur.description]
					if len(col_nms) >= index_col-1:
						col_nm = col_nms[index_col-1]
						# print("CREATE INDEX ind_{0} ON {1}({0});".format(col_nm,tbl_nm))
						cur.execute("CREATE UNIQUE INDEX ind_{0} ON {1}({0});".format(col_nm,tbl_nm))
			ret = True
		else:
			raise Exception('db file does not exist')
	except Exception as e:
		raise Exception(e)
	finally:
		return ret
		if con:
			con.close()

def logRecord(db,tbl_nm,*to_log):
	"""
	log supplied values
	surplus fields are truncated if necessary
	return True if OK
	"""
	if to_log:
		try:
			if os.path.isfile(db):
				con = sqlite3.connect(db)
				cur = con.cursor()
				
				# get number of columns
				cur.execute('PRAGMA table_info({0});'.format(tbl_nm))
				col_nr = len(cur.fetchall())
				
				# insert values (scraping surplus values)
				qr_placeholders = ','.join(['?' for i in range(col_nr)])
				cur.execute('INSERT INTO {0} VALUES ({1});'.format(tbl_nm,qr_placeholders),to_log[:col_nr])

				con.commit()
				return True
			else:
				raise Exception('db file does not exist')
		except Exception as e:
			raise Exception(e)
		finally:
			if con:
				con.close()


# @@@ upravit, aby umělo: vybrat sloupce, seřadit podle sloupců, limit nebo bez
def readLatestRecord(db:str,tbl_nm:str,order_by_col_nr_or_nm,asc_desc:str)->list:
	"""
	list of latest record
	field #1 = time difference (in seconds, integer) between now and datetime read from a log tbl
	the rest of the fields remain intact
	if no record is found, None is returned
	"""
	
	try:
		if os.path.isfile(db):
			con = sqlite3.connect(db)
			cur = con.cursor()
			
			# get column 1 name
			# cur.execute("SELECT * FROM {0} LIMIT 1;".format(tbl_nm))
			# col_nm = [description[0] for description in cur.description][0]

			# ORDER BY 2 ASC to get the latest date(time); 2 for the first regular column (disregarding the extra added column)
			cur.execute('SELECT * FROM {0} ORDER BY {1} {2} LIMIT 1;'.format(tbl_nm,order_by_col_nr_or_nm,asc_desc.upper()))
			fetched_res = cur.fetchone()
			return list(fetched_res) if fetched_res else None
		else:
			raise Exception('db file does not exist')
	except Exception as e:
		raise Exception(e)
	finally:
		if con:
			con.close()