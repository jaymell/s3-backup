#!/usr/bin/python

import boto
import os

CRED_BUCKET = 'jaymell-cred'
HOME = os.environ.get('HOME')
CRED_PATH = os.path.join(HOME,'.ssh')
con = boto.connect_s3()
bucket = con.get_bucket(CRED_BUCKET)

for item in bucket.list():
	key = str(item.key)
	dest_file = os.path.join(CRED_PATH,key)
	if not os.path.exists(dest_file):
		item.get_contents_to_filename(dest_file)
		os.chmod(dest_file,0600)
