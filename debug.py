from general_utils import *
from shared_constants import *
dropbox_token = readTabbedFile(absFilePath(CREDENTIALS_DROPBOX_FL))[0]
drop = Drop(dropbox_token)

x = drop.uploadTempFile(local_fl_nm='/home/gilbert/Downloads/2017-04-22_home_gilbert_downloads.txt')
print(x)
