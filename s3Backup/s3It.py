import subprocess 
import shlex

def s3It(source, dest, isDir=False):
	""" source is file by default, possibly directory;
		torage-class STANDARD_IAestination is the bucket URL """

	if isDir == False:
		cmd = 's3cmd put --server-side-encryption --storage-class STANDARD_IA %s %s' % (source, dest)
	else:
		cmd = 's3cmd put --recursive --server-side-encryption --storage-class STANDARD_IA %s %s' % (source, dest)

	proc=subprocess.Popen(shlex.split(cmd),stdout=subprocess.PIPE)
	out,err=proc.communicate()

	return(out, err)
