#!/usr/bin/python

import sys
import os

if len(sys.argv) != 3:
    print "Usage: " + sys.argv[0] + " DATA_DIR RESULT_DIR"
    sys.exit()
    
data_dir = sys.argv[1]
result_dir = sys.argv[2]

for dirpath, dirnames, filenames in os.walk(data_dir):
	for filename in filenames:
		if filename[-4:].lower() == '.pst':
			print filename
			
			out_dir = os.path.join(result_dir, filename[:-4])
			os.mkdir(out_dir)
			os.system('readpst -So "' + out_dir + '" "' + os.path.join(dirpath, filename) + '"')

