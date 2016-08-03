from __future__ import print_function
import tarfile
import sys
import os
import datetime
import sys
import socket
import re

def isMatch(f, excludes):
    match = False
    for i in excludes:
        match = re.match('^%s.*' % os.path.realpath(i), os.path.realpath(f))
        if match: break
    return match
    

def can_read(f):
   """ to prevent failure but still print file name if reads fail """
   if not os.access(f, os.R_OK):
     print("Failed adding %s -- permission denied" % f, file=sys.stderr)
     return False

   return True

def tarIt(source, destDir, excludes=[]):
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
            out.add(source, recursive=True, exclude = lambda x: True if (isMatch(x, excludes) or not can_read(x)) else False)
        else:
            out.add(source, recursive=True)
        
	print('Successfully created archive %s' % destFile)
	return destFile
