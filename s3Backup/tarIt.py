import tarfile
import sys
import os
import datetime

def tarIt(source, destDir):
	""" take directory, tar it, put it in destination
		folder, file name generated from directory, replacing
		special characters with underscores; one success,
		return name of archive created """

	now = datetime.datetime.now()
	destFile = os.path.join(destDir,source.replace('/','_').replace(' ','_')) + '-' + now.strftime('%Y%m%d_%s') + '.tar.gz'
	out = tarfile.open(destFile, 'w:gz')
	# add files:
	out.add(source, recursive=True)
	print('Successfully created archive %s' % destFile)
	return destFile
