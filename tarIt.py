from __future__ import print_function
import tarfile
import sys
import os
import datetime
import sys
import socket
import utils

def TarIt(source, destDir, excludes=[]):
	""" take directory, tar it, put it in destination
		folder, file name generated from directory, replacing
		special characters with underscores; one success,
		return name of archive created """

	now = datetime.datetime.now()
        destFile = os.path.join(
            destDir, 
            socket.gethostname() + '-' + source.replace('/','_').replace(' ','_') + '-' + now.strftime('%Y%m%d-%s') + '.tar.gz'
        )
	out = tarfile.open(destFile, 'w:gz')
        if excludes:
            # exclude if we told it to exclude it or
            out.add(source, recursive=True, exclude = lambda x: True if (utils.is_match(x, excludes) or not utils.can_read(x)) else False)
        else:
            out.add(source, recursive=True)
        
	print('Successfully created archive %s' % destFile)
	return destFile
