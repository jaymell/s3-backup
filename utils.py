from __future__ import print_function
import re
import os
import sys

def is_match(f, excludes):
    match = False
    for i in excludes:
        match = re.match('^%s.*' % i, f)
        if match: break
    return match


def can_read(f):
   """ return False and print file name to stderr if can't read
   """
   if not os.path.exists(f):
     print("%s does not exist" % f, file=sys.stderr)
     return False
   if not os.access(f, os.R_OK):
     print("%s -- permission denied" % f, file=sys.stderr)
     return False
   return True


def clean_paths(path_list):
  """ clean up excluded paths """
  cleaned_paths = []

  for path in path_list:
    path = os.path.abspath(os.path.expanduser(path))
    if can_read(path):
      cleaned_paths.append(path)
  return cleaned_paths

