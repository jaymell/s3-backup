#!/usr/bin/python

import ConfigParser
import sys
import os
import tarIt
import s3It
import datetime
import argparse

""" assumes you have access credentials to bucket set up for
user running this script  -- above config file is just for
bucket name """

argparser = argparse.ArgumentParser(description='Backup directories to s3')
argparser.add_argument("-d", "--dest", action="store", help="destination s3 folder")
argparser.add_argument("source_list", nargs="+")
args = argparser.parse_args()

tarDest = '/home/backup/stage'
config = './s3.cfg'
parser = ConfigParser.SafeConfigParser()

try:
	parser.read(config)
	s3Dest = parser.get('destination', 's3_bucket')
except Exception as e:
	print('Unable to read config file: %s' % e)
	sys.exit(1)

# add destination to s3 bucket url if specified:
if args.dest:
	s3Dest += args.dest 
# make sure s3 knows the destination is a directory:
if s3Dest[-1] != '/': s3Dest += '/'

# it would be cool to do this in multiple threads:
for source in args.source_list: 

	now = datetime.datetime.now()
	print('Beginning backup of %s: %s' % (source, now))
	try:
		tarFile = tarIt.tarIt(source, tarDest)
	except Exception as e:
		print('Failed to create archive: %s' % e)
		sys.exit(3)

	now = datetime.datetime.now()
	print('Beginning s3 sync of %s: %s' % (tarFile, now))
	try:
		s3It.s3It(tarFile, s3Dest)
	except Exception as e:
		print('Failed to send %s to s3: %s' % (tarFile, e))	
	else:
		now = datetime.datetime.now()
		print("Success: Archive %s created and sent to s3 at %s" % (tarFile, now))

	try:
		os.remove(tarFile)
	except Exception as e:
		print('Failed to delete local copy of archive: %s' % e)
		
	now = datetime.datetime.now()
	print('Completed at %s' % now)

