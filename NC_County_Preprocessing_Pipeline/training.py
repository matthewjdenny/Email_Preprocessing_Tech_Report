import os
import sys
def mark_as_spam(criterion,directory_name):
	for path,subdirs,files in os.walk(directory_name):
		for filename in files:
			f_name = os.path.join(path,filename)
			print f_name
			command = ""
			if criterion == "spam":
				print "spam"
				command = "bogofilter -s -v < " + f_name
			elif criterion == "ham":
				print "ham"
				command = "bogofilter -n -v < " + f_name
			os.system(command)
mark_as_spam(sys.argv[1],sys.argv[2])
