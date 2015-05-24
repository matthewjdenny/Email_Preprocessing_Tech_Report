#!/usr/bin/python

#TODO
#need to check on filtering on lines 71-73

"""
Given an input directory, a stopword file, and an output location,
this script parses the email messages in the directory and writes
a pickle file that can subsequently be consumed by one of the
matrix writer scripts.
"""

import sys
import os
import re
import pickle
import email.parser
import email.utils
import time

import text_utilities

__DEBUG__ = False

parser = email.parser.Parser()

file_re = re.compile('^\d+\.?$')

CountyCustom = True #activates a module that replaces county specific email addresses with others such as gpoor@transylvaniacounty.org with gay.poor@transylvaniacounty.org

COUNTYEXTENSION = '@mcdowellgov.com' # the extension to be used for the current county
#CountyStop = COUNTYEXTENSION + '$' #adds a $ sign to the end for use in some regular expressions

#modified for McDowell and its multiple email address endings
CountyStop = '(@mcdowellgov.com|@mcdowellpubliclibrary.org|@titlesearcher.com|@mcdowellsheriff.org|@mcdowell.nc.gov|@mcdowellems.com)'+ '$'


validNames = [] #keep track of who has a valid @transylvaniacounty.org email address

def parse_path(path, stop_words, filter_addr_fn = None):
	emails = []
	if os.path.isdir(path):
		for filename in os.listdir(path):
			emails += parse_path(os.path.join(path, filename), stop_words, filter_addr_fn = filter_addr_fn)
	else:
		filename = os.path.basename(path)
		if not file_re.match(filename):
			if __DEBUG__:
				print >> sys.stderr, "File " + filename + " is not in the expected \d+. filename format. Skipping..."
		else:
			#print "Now Parsing email: "+ filename
			e = parser.parse(open(path))
			e = process_email(e, stop_words, filename = filename, filter_addr_fn = filter_addr_fn)

			if e != None:
				e['file'] = path
				emails = [e]

	return emails

unique_emails = set()

def process_email(email, stop_words, filename, filter_addr_fn = None ):
	e = {}
	#deal with ed davis special case
	#if email.get_all('From') == '\"Davis, Edward - Whiteville, NC\" <MAILER-DAEMON>':
		#temp = "edavis@columbusco.org"
		#e['from'] = parse_addresses(temp, filename = filename)
	e['from'] = parse_addresses(email.get_all('From'), filename = filename)
	if e['from'] == []:
		e['from'] = parse_addresses(email.get_all('X-From'), filename = filename)
#	I'm not sure about this tag and we don't use it anyway
#	e['senders'] = parse_addresses(email.get_all('Sender'))
	if email.get_all('To') != "undisclosed-recipients:;":
		e['to'] = parse_addresses(email.get_all('To'), filename = filename)
		if e['to'] == []:
			e['to'] = parse_addresses(email.get_all('X-To'), filename = filename)
	e['cc'] = parse_addresses(email.get_all('Cc'), filename = filename)
	if e['cc'] == []:
		e['cc'] = parse_addresses(email.get_all('X-cc'), filename = filename)

	if filter_addr_fn:
		e['from'] = filter_addr_fn(e['from'])
		e['to'] = filter_addr_fn(e['to'])
		e['cc'] = filter_addr_fn(e['cc'])

#	if not e['from'] or (not e['to'] and not e['cc']):
#		print "Skipping..."
#		return None

	#changed to deal with emails that have no date
	if email.get('date') != None:
		if email.get('date') == "Feb 23, 2011 at 3:26 PM":
			print "date problem with email: " + filename
		e['date'] = email.get('date')	
	else:
		if email.get('sent') != None:
			temp = email.get('sent')
			if email.get('sent') == "Feb 23, 2011 at 3:26 PM":
				print "date problem with email: " + filename
			temp = temp + " -0500"
			#print temp
			#if not address_re1.search(temp):
				#print "this email has a messed up date: "+ filename
			e['date'] = temp
		else:	
			print "this email has no date: " + filename
	#had to change this to deal with emails with no subject
	if email.get('subject') != None:	
		e['subject'] = parse_text(email.get('subject'), stop_words)
	else:
		e['subject'] = "No Subject"
		print "No subject for email: " + filename
	# Check that this is a unique message
	meta_data = str([e['from'], e['to'], e['cc'], e['subject'], e['date']])
	if meta_data in unique_emails:
		return None
	else:
		unique_emails.add(meta_data)

#	I don't know about the Thread ID and we aren't using it for
#	this project anyway
#	e['thread'] = (email.get('Thread-Index' or email.get('thread-index')))

	# Extract the plaintext message from the tree of different body MIME types
	message = email
	while True:
		try:
			message = message.get_payload(0)
		except:
			break
	message = message.get_payload()
	e['message'] = parse_message(message, stop_words)

	return e

address_re1 = re.compile('\s*,\s*|\s*;\s*') #finds a comma or semicollon with any number of spaces on iether side of it and splits the string on that 
address_re2 = re.compile('<\.?(.*)>') #finds things in < > including email addresses
address_re3 = re.compile('^[a-zA-Z0-9&\'*+_\-.@/=?^{}~]+@[a-zA-Z0-9_\-.~]+\.[a-zA-Z\.]+$') #this will get an email address of type sombody@somecounty.org
address_re4 = re.compile('<MAILER-DAEMON>') #deal with Mailer Daemon
address_re5 = re.compile("([a-zA-Z0-9_&\.\s\'\-]+)") #Finds names in quotations that include a:    _ & . space ' or - but not a comma
address_re6 = re.compile("([a-zA-Z,&_\.\s\'\-]+)") #Finds names in quotations with a comma in the name (this screws things up)
address_re7 = re.compile('/@/g') #Finds @
address_re8 = re.compile('\((^[a-zA-Z0-9&\'*+_\-.@/=?^{}~]+@[a-zA-Z0-9_\-.~]+\.[a-zA-Z\.]+$)\)') #finds an email that is enclosed in parentheses like: (sombody@somecounty.org)
address_re9 = re.compile('[\s]+') #finds any number of spaces
address_re10 = re.compile('[a-zA-Z]') #finds the first letter of the word


def parse_addresses(string, filename):
	addresses = []

	if string != None:
		line = string[0]
		#print "The raw text is: " + line  #shows us which emails are getting passed in
		
		#need to preprocess to make sure that if we have "Graham, Robert" <RGraham@ci.charlotte.nc.us> we do not split on the comma so we transform it to "Robert Graham" <RGraham@ci.charlotte.nc.us>
		match = address_re6.search(line)
		if match:
			temp = match.group(1) 
			badComma  = address_re1.search(temp) #if we find a comma in the name
			if badComma: #we need to remove it
				#print "this name has a bad comma: " + temp
				temp2 = address_re1.split(temp) #split on the comma
				#for l in temp2:
					#print l
				replacement = temp2[1] + " " + temp2[0] #put the first name first and the second second
				#print "the replcement is " + replacement
				line = line.replace(temp, replacement) #switch out the correct name with the problem name in the line
				
				
		
		strings = address_re1.split(line) #split the string on commas or semicolons so we can process individual emails
		
		
		#deal with case where it is an internal email and there is no address
		cur = 0
		for s in strings:
			#print "The full string is: " + s
			internalEmail = address_re4.search(s) #if we find a <MAILER-DAEMON> as part of the string
			if internalEmail:  
				match = address_re5.search(s)
				if match:
					s = match.group(1)
					validNames.append(s) # add to a list of people with vaid transylvania email addresses
				s = s.replace (" ", ".")
				#print "The corrected string is: " + s
				replacement = "<" + s + COUNTYEXTENSION + ">" #need to change this for different counties
				#print "replacement: " +  replacement
				validNames.append(replacement) # add to a list of people with vaid transylvania email addresses
				strings[cur] = replacement
			else:
				
				
				Address = address_re2.search(s) #see if there is a valid email address in < > in the string
				Address2 = address_re3.search(s) # check in there is a ready to go address with no <> on either side
				if not Address and not Address2: #if not then we need to create one from the name, this deals with people in the from column in transylvania
					match = address_re5.search(s)
					if match:
						s = match.group(1)
						# This is meant specifically for columbus
						#s = s.replace (" ", ".") # this is commented out jsut for columbus
						s = s.replace ("\'", "")
						s = s.lstrip()
						#hasspace = address_re9.search(s)
						#altered for McDowell
						hasspace = 0
						if hasspace == 1:
							#print s
							s = address_re9.split(s)
							if len(s) > 0:
								a = s[0]
								b = s[1]
								if type(s[1]) == None or type(s[0]) == None:
									print "This is a problem"
								else: 	
									if len(s) > 1 & isinstance(s[1], str) :
										#if isinstance(s[1], str) :
										s = str(s)
										firstletter = str(a)
										#print "first letter " + firstletter
										firstletter = address_re10.match(firstletter)
										#print "first letter " + firstletter.group(0)
										#s = firstletter.group(0)
										#if isinstance(s[2], str) :	
										lastname = str(b)
										#print "last name " + lastname
										#s = lastname
										#if isinstance(s[1], str) &  isinstance(s[2], str):	
										s = firstletter.group(0) + lastname
										s = s.lower()
						#print "The corrected string is: " + s
						replacement = "<" + s + COUNTYEXTENSION + ">"  #need to change this for different counties
						#print "replacement for an email with multiple internal recipents: " +  replacement
						strings[cur] = replacement
				
			cur = cur + 1
	
		#add emails to the database (this is the main functionality)
		for s in strings:
			# Extract email address from strings of the form "Jim Smith" <jsmith@example.com>
			match = address_re2.search(s)
			if match:
				s = match.group(1)
			
			# Extract email address from strings of the form "Jim Smith" (<jsmith@example.com>)	
			match2 = address_re8.search(s)
			if match2:
				s = match2.group(1)

			# Search for illegal characters (especially spaces)
			s = s.replace("<", '')
			s = s.replace(">", '')
			s = s.replace(".net.", ".net")
			s = s.replace(".edu.", ".edu")
			s = s.replace(".com.", ".com")
			s = s.replace(".org.", ".org")
			s = s.replace(" ", '')
			s = s.replace("\'", '')
			s = s.replace('\n', '')
			
			
			#if everything looks good then we add it
			if address_re3.match(s):
				
				s = s.lower()

				if CountyCustom:
					if s == "alisonmorgan-mcdowellcountyfinance@mcdowellgov.com":
						s = "amorgan@mcdowellgov.com"
					if s == "ashleywooten@mcdowellgov.com" or s == "ashleyr.wooten@mcdowellgov.com" :
						s = "awooten@mcdowellgov.com"
					if  s == "carrie.padgett@mcdowellgov.com" or s ==  "lindaonufreycarrie.padgett@mcdowellgov.com" :
						s = "cpadgett@mcdowellgov.com"
					if s == "cabernathy@mcdowellgov.com" or s == "chuckabernathy@mcdowellgov.com":
						s = "charlesa@mcdowellgov.com"
					if s == "keithrenfro@mcdowellgov.com":
						s = "krenfro@mcdowellgov.com"
					if s == "philliphardin@mcdowellgov.com" or s ==  "hardin@mcdowellgov.com" or s == "phillip.hardin@mcdowellgov.com":
						s = "phillip.hardin@mcdowell.nc.gov"
					if s == "suehuskins@mcdowellgov.com" or s ==  "susanhuskins@mcdowellgov.com":
						s = "sue.huskins@mcdowellgov.com"
					if s == "terrydepoyster@mcdowellgov.com":
						s = "terryd@mcdowellgov.com"
					if s == "williamkehler@mcdowellgov.com":
						s= "wkehler@mcdowellems.com"
					if s == "dudleygreene@mcdowellgov.com":
						s = "dgreene@mcdowellsheriff.org"
					if s == "elizabethhouse@mcdowellgov.com":
						s= "ehouse@mcdowellpubliclibrary.org"
					if s == "mikegladden@mcdowellgov.com":
						s ="mike.gladden@mcdowellgov.com"
					if s == "robbinsilvers@mcdowellgov.com " or s ==  "robbin@mcdowellgov.com" :
						s= "rsilvers@mcdowellgov.com"
					if s == "terryyoung@mcdowellgov.com" or s ==  "young@mcdowellgov.com":
						s = "terry.young@mcdowellgov.com"
				
				print s
				addresses.append(s.lower())
			else:
				print "Bad email string: " + s + " in email number: " + filename
			#elif __DEBUG__:
				#print >> sys.stderr, "Bad email string: " + s

	return addresses

#dont know if this should be @transylvaniacounty.org

filter_re1 = re.compile(CountyStop)

def filter_addresses(addr):
	return filter(lambda x: filter_re1.search(x), addr)
	
#message_re1 = re.compile('\S[IMAGE]\S') #original
message_re1 = re.compile('\S"IMAGE"\S') #updated so it will not remove all caps words. 
message_re2 = re.compile('[\n\r]+') #newline
# I'm not going to remove forward headers, at Peter's request
#message_re3 = re.compile('\s*(?:[<|]?[-=_*.]{8}|-+-alt---boun|-+---boundary|-+----\s?Inline|\??-+----\s?Origina|-+----\s?Forwarded |-+----\s?Begin forward|Enron on .*-+)', flags=re.IGNORECASE)
message_re3 = re.compile('\s*(?:[<|]?[-=_*.]{8}|-+-alt---boun|-+---boundary|-+----\s?Inline|\??-+----\s?Origina|Enron on .*-+)', flags=re.IGNORECASE) #finds boundaries between emails in a thread
message_re4 = re.compile('\s*(?:From:|To:)') # look for from or to tags
message_re5 = re.compile('\s*>') #looks for the end of an email address
message_re6 = re.compile("This is a receipt for the mail you sent to")

def parse_message(message, stop_words):
	# Remove all image tags
	message = message_re1.sub('', message)

	# Split the message on newline boundaries
	lines = message_re2.split(message)

	result = []
	for i in range(len(lines)):
		# Look for forward/reply-to delimiters and cut off the message
		if message_re3.match(lines[i]):
			break
		
		#do not capture information in the reply receipt that will jsut list a bunch of emails.
		if message_re6.match(lines[i]):
			break

		# Sometimes there are no delimiters except a 
		# On Tuesday ... blah blah
		# From: 
		elif len(lines) > i+1 and message_re4.match(lines[i+1]):
			break
		# Look for lines beginning with >, as they are probably quoted text
		elif not message_re5.match(lines[i]):
			result.append(lines[i])

	# Tokenize
	message = parse_text('\n'.join(result), stop_words)

	return message

def parse_text(line, stop_words):
	# Exact copy of Peter's original method
	line = line.strip()
	words = line.split(' ')
	url_tags = ['<htt', 'http', '<www', 'www.', '.com','.net','.org','.gov',
		'.edu','.com>', '.net>','.org>','.gov>','.edu>']
	remove = map(lambda x: x[:4] in url_tags or x[-4:] in url_tags or
		x[-5:] in url_tags, words)
	words = [words[i] for i in range(len(words)) if not remove[i]]
	junk_tags = ['!SIG']
	remove = map(lambda x: x[:4] in junk_tags, words)
	words = [words[i] for i in range(len(words)) if not remove[i]]
	junk_tags = ['DTSTAMP:','CREATED:','LAST-MOD','DTSTART;','DTEND;VA']
	remove = map(lambda x: x[:8] in junk_tags, words)
	words = [words[i] for i in range(len(words)) if not remove[i]]
	line = ' '.join(words)
	line = text_utilities.nice(line, stop_words)
	return(line)

def compare_email_dates(a, b):
	"""
	Compares email-format dates for sorting
	"""
	#print "Current A:" + a['date'] 
	#print "Current B:" + b['date'] 
	a_date = time.mktime(email.utils.parsedate(a['date']))
	b_date = time.mktime(email.utils.parsedate(b['date']))

	return cmp(a_date, b_date)

if __name__ == '__main__':
	if len(sys.argv) < 5:
		print >> sys.stderr, "Usage: " + sys.argv[0] + " IN_DIR STOP_WORDS_FILE OUT_PICKLE_FILE PERSONAL_FOLDER "
		sys.exit()

	IN_DIR = sys.argv[1]
	STOP_WORDS_FILE = sys.argv[2]
	OUT_PICKLE_FILE = sys.argv[3]
	PERSONAL_FOLDER = sys.argv[4]
	#VALID_EMAIL_OUTDIR = sys.argv[5] if len(sys.argv) > 5 else 'TRUE' #argument to optionally write validated email file

	if not os.path.isdir(IN_DIR):
		print >> sys.stderr, IN_DIR + " is not a valid directory"
		sys.exit()

	stop_words = []
	stop_word_file = open(STOP_WORDS_FILE)
	for l in stop_word_file:
		stop_words += [l.strip()]
	stop_word_file.close()

	emails = []

	#if there is a personal folder in each person's directory so the directory path is : County/Person/Personal/Subfolders/emails
	if PERSONAL_FOLDER == 'TRUE':
		for person in os.listdir(IN_DIR): #for every person's folder
			print 'Current Person ' + person + ' ...' 
			if person != '.DS_Store':
				for folder in os.listdir(os.path.join(IN_DIR, person)):
					print 'Personal Folder ' + folder + ' ...' 
					if folder != '.DS_Store':
						for personal in os.listdir(os.path.join(IN_DIR, person, folder)):
							if (personal != 'Contacts') and (personal != 'Calendar') and (personal != '.DS_Store'):
			
								print '-' * (len(personal) + 12)
								print 'Parsing ' + personal + ' ...'
								print '-' * (len(personal) + 12)

								#Parse all of the emails in each directory
								emails += parse_path(os.path.join(IN_DIR, person, folder, personal), stop_words)
							else:
								print 'Not Parsing ' + personal + ' ...'
		
	#if there is not a personal folder in the directory	
	else:	
		for folder in os.listdir(IN_DIR):
			print '-' * (len(folder) + 12)
			print 'Parsing ' + folder + ' ...'
			print '-' * (len(folder) + 12)

			#Parse all of the emails in each directory
			emails += parse_path(os.path.join(IN_DIR, folder), stop_words)

	print "Emails: " + str(len(emails))

	print "Sorting (this may take a while...)"

	emails = sorted(emails, cmp=compare_email_dates)

	print "Saving pickle..."

	pickle_file = open(OUT_PICKLE_FILE, 'w')
	pickle.dump(emails, pickle_file)
	pickle_file.close()
	
	
 


