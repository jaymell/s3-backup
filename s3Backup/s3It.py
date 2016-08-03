#!/usr/bin/python

import boto3
import s3transfer
import sys
import os

import subprocess
import shlex

#syntax: 
## old: python s3It.py FILE 's3://<bucket-name>' <-- no special URL in bucket-name
## boto3: python s3It.py FILE <bucket-name> <-- no special URL in bucket-name, but
##	this has only been tested with us-east-1 buckets

def olds3It(source, dest, isDir=False):
  """ source is file by default, possibly directory;
      storage-class STANDARD_IAestination is the bucket URL """

  if isDir == False:
    cmd = 's3cmd put --server-side-encryption --storage-class STANDARD_IA %s %s' % (source, dest)
  else:
    cmd = 's3cmd put --recursive --server-side-encryption --storage-class STANDARD_IA %s %s' % (source, dest)

  proc = subprocess.Popen(shlex.split(cmd),stdout=subprocess.PIPE)
  out, err = proc.communicate()

  return(out, err)

def s3It(source, bucket):
  """ if source is file, push to s3;
  if directory, traverse and upload
  """
  try:
    s3 = boto3.client('s3')
    transfer = s3transfer.S3Transfer(s3)
  except Exception as e:
    print("Failed to start client: %s" % e)
    sys.exit(1)

  if os.path.isfile(source):
    _source = os.path.basename(source)
    try:
      transfer.upload_file(source, bucket, _source) 
    except Exception as e:
      print("Upload of %s failed: %s" % (source, e))
  elif os.path.isdir(source):
    print("Havent actually implemented this yet... come back soon!")
    sys.exit(2)
  else:
    print("I dont know what to do with source... exiting")
    sys.exit(3)

if __name__ == '__main__':
	try:
		source = sys.argv[1]
		dest = sys.argv[2]
	except:	
		print("Usage: %s source bucket-name" % sys.argv[0])
		sys.exit(1)
	else:
		s3It(source, dest)
