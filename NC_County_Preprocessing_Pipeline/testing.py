import os
import sys
import email.parser
import email.utils
import csv

# Take the county Name as input
# Take the input directory as input
# Have a global variable called as system path.

# This is a function to classify things.
def classify(input_directory):
	global COUNTY, OUTPUT_PATH
	output_directory = OUTPUT_PATH 
	# Check if the output directory exists.
	# If it doesn't exist make one
	# Make the spam directory
	# Make the ham directory
	
	if not os.path.isdir(output_directory):
		os.system("mkdir " + output_directory )
		os.system("mkdir " + output_directory + "/" + "ham")
		os.system("mkdir " + output_directory + "/" + "spam")
		os.system("mkdir " + output_directory + "/" + "unsure")
	# You need to have logic to check whether it is a valid file or not
	total = 0
	for path,subdirs,files in os.walk(input_directory):
		for filename in files:
			f_name = os.path.join(path,filename)
			if (COUNTY == "Polk" or COUNTY == "Hoke" or COUNTY == "Randolph") and filename[-3:] != "eml":
		                continue
            		elif COUNTY == "Montgomery" and filename[:2] != "xx":
		                continue
            		elif COUNTY == "Duplin" and filename[-4:] != "imap":
		                continue
            		elif COUNTY == "Columbus" and filename[-3:] != "MAI":
		                continue
            		elif COUNTY != "Polk" and COUNTY != "Montgomery"  and COUNTY != "Hoke" and COUNTY != "Randolph" and COUNTY != "Columbus" and COUNTY!="Duplin" and not filename.isdigit():
		                continue
			if "Calendar" in f_name or "Contacts" in f_name:
				continue
			print f_name
			replaced_fname = f_name.replace(" ","\ ")
			replaced_fname = replaced_fname.replace("'","\\\'")
			replaced_fname = replaced_fname.replace("(","\\(")
			replaced_fname = replaced_fname.replace(")","\\)")
			#command = "bogofilter -p -e < " + f_name + " | grep \"X-Bogosity: Ham, tests=bogofilter,\" "
			if total <0:
				command = "bogofilter -p -u -e < " + replaced_fname + " > trial.txt"
			else:
				command = "bogofilter -p -e < " + replaced_fname + " > trial.txt"
			parse = os.system(command)
			command = "grep \"X-Bogosity: Ham, tests=bogofilter,\" trial.txt"
			all1 =os.system(command)
			command = "grep \"X-Bogosity: Spam, tests=bogofilter,\" trial.txt"
			all2 =os.system(command)
			command = "grep \"X-Bogosity: Unsure, tests=bogofilter,\" trial.txt"
			all3 =os.system(command)
			if not all1:
				# Means it is ham move to ham folder.
				print "Ham",f_name
				command = "cp " + replaced_fname + " " + output_directory + "/ham/"+str(total)
				os.system(command)
				print command
			elif not all2:
				# Means it is spam move to spam folder.
				print "Spam",f_name
				command = "cp " + replaced_fname + " " + output_directory + "/spam/" +str(total)
				os.system(command)
				print command
			elif not all3:
				# Means it is unsure move to unsure folder.
				command = "cp " + replaced_fname + " " + output_directory + "/unsure/" + str(total)
				print "Unsure",f_name
				print command
				os.system(command)
			total=total+1
		
	
def obtainFromEmail(email):
    return email.get_all("From")
    
def obtainSubjectEmail(email):
    return email.get_all("subject")
    
# Function to conclude about unsure emails. Use two semantics.
def move_files(from_where):
	valid_names=[]
	COUNTY_NAMES = ["wilkes","polk","vance","transylvania","person","nash","chatham","mcdowell","lincoln","lenoir","dare","camden","caldwell","chowan","jackson","alexander","poke","montogmery","hoke","duplin","columbus","randoplh"]
	print COUNTY_NAMES
	COUNTY_NAMES = COUNTY_NAMES+ valid_names
	print COUNTY_NAMES
	parser = email.parser.Parser()
	global COUNTY, OUTPUT_PATH,COUNTY_EXTENSION
	output_directory = OUTPUT_PATH
	if from_where == "spam":
		input_directory = output_directory + "/spam"
	else:
		input_directory = output_directory + "/unsure"
	# You know the input directory. from the input specified to this function.
	# Loop through all the files of the input directory..
	for path,subdirs,files in os.walk(input_directory):
		for filename in files:
	# First initialize valid to zero.
			f_name = os.path.join(path,filename)
			print f_name
			replaced_fname = f_name.replace(" ","\ ")
			valid =0
			emaildata= parser.parse(open(f_name,"r"))
			subject = obtainSubjectEmail(emaildata)
			sender = obtainFromEmail(emaildata)
			if subject == None or sender == None:
				continue
			subject = subject[0].lower()
			sender = sender[0]
			print subject,sender,COUNTY_EXTENSION
			if  (COUNTY_EXTENSION in sender) or "re:" in subject or "MAILER-DAEMON" in sender or "fw" in subject or "county" in sender or "@" not in sender:
				print subject,sender,COUNTY_EXTENSION,valid
				valid =1
	# If sender is from nash county . Make the valid 1
	# If the mail was a reply or forward make the valid 1
			for name in COUNTY_NAMES:
				if name in sender:
					valid=1
					break
			print valid
			if valid:
				print "Found"
				if from_where == "spam":
					command = "bogofilter -Sn -v < " + replaced_fname
					#os.system(command)
					print command
				elif from_where == "unsure":
					command = "bogofilter -n -v < " + replaced_fname 
					#os.system(command)
					print command
				command = "mv " + replaced_fname +  " " + output_directory + "/ham/"
				print command
				os.system(command)
					


def select_county_extension():
    global COUNTY,COUNTY_EXTENSION
    if COUNTY == "Wilkes":
        COUNTY_EXTENSION = "wilkescounty.net"
    elif COUNTY == "Vance":
        COUNTY_EXTENSION = "vancecounty.org"
    elif COUNTY == "Transylvania":
        COUNTY_EXTENSION = "transylvaniacounty.org"
    elif COUNTY == "Person":
        COUNTY_EXTENSION = "personcounty.net"
    elif COUNTY == "Nash":
        COUNTY_EXTENSION = "nashcountync.gov"
    elif COUNTY == "McDowell":
        COUNTY_EXTENSION = "mcdowellgov.com"
    elif COUNTY == "Lincoln":
        COUNTY_EXTENSION = "lincolncounty.org"
    elif COUNTY == "Lenoir":
        COUNTY_EXTENSION = "co.lenoir.nc.us"
    elif COUNTY == "Dare":
        COUNTY_EXTENSION = "darenc.com"
    elif COUNTY == "Camden":
        COUNTY_EXTENSION = "camdencountync.gov"
    elif COUNTY == "Caldwell":
        COUNTY_EXTENSION = "caldwellcountync.org"
    elif COUNTY == "Chowan":
        COUNTY_EXTENSION = "chowan.nc.gov"
    elif COUNTY == "Jackson":
        COUNTY_EXTENSION = "jacksonnc.org"
    elif COUNTY == "Alexander":
        COUNTY_EXTENSION = "alexandercountync.gov"
    elif COUNTY == "Polk":
        COUNTY_EXTENSION = "polknc.org"
    elif COUNTY == "Montgomery":
        COUNTY_EXTENSION = "montgomerycountync.com"
    elif COUNTY == "Hoke":
        COUNTY_EXTENSION = "hokecounty.org"
    elif COUNTY == "Duplin":
        COUNTY_EXTENSION = "duplincountync.com"
        # large scale says for huge counties do not generate the edge matrix.
    elif COUNTY == "Columbus":
        COUNTY_EXTENSION = "columbusco.org"
    elif COUNTY == "Camden":
        COUNTY_EXTENSION = "camdencountync.gov"
    elif COUNTY == "Randolph":
        COUNTY_EXTENSION = "co.randolph.nc.us"
    else:
        COUNTY_EXTENSION = ""

# Initialize variables COUNTY, OUTPUT_PATH with the input directory.
COUNTY = sys.argv[1]
select_county_extension()
print COUNTY_EXTENSION
OUTPUT_PATH= sys.argv[3]
OUTPUT_PATH = OUTPUT_PATH.replace(' ','\ ')
# first function call to classify everything.
classify(sys.argv[2])
# Second function call to move from unsure to ham
move_files("unsure")
# Third function call to move from spam to ham
move_files("spam")
