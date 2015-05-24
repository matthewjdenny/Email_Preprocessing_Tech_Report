#usr/bin/python

################################## Code Expectation ################################
# This code contains all modules required to process text element of an e-mail
###################################################################################

import sys
import re
import email_scan

name_mapping={}
email_counts={}


# These set of regular expressions are no more used.
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


#message_re1 = re.compile('\S[IMAGE]\S') #original
message_re1 = re.compile('\S"IMAGE"\S') #updated so it will not remove all caps words. 
message_re2 = re.compile('[\n\r]+') #newline
# I'm not going to remove forward headers, at Peter's request
#message_re3 = re.compile('\s*(?:[<|]?[-=_*.]{8}|-+-alt---boun|-+---boundary|-+----\s?Inline|\??-+----\s?Origina|-+----\s?Forwarded |-+----\s?Begin forward|Enron on .*-+)', flags=re.IGNORECASE)
message_re3 = re.compile('\s*(?:[<|]?[-=_*.]{8}|-+-alt---boun|-+---boundary|-+----\s?Inline|\??-+----\s?Origina|Enron on .*-+)', flags=re.IGNORECASE) #finds boundaries between emails in a thread
message_re4 = re.compile('\s*(?:From:|To:)') # look for from or to tags
message_re5 = re.compile('\s*>') #looks for the end of an email address
message_re6 = re.compile("This is a receipt for the mail you sent to")
message_re7 = re.compile("<.*>")
message_re8 = re.compile(r'<.*?>')
message_re9 = re.compile(r'{.*?}')
message_re10 = re.compile(r'----- Original Message ---')
_link = re.compile(r'(?:(http://)|(www\.))(\S+\b/?)([!"#$%&\'()*+,\-./:;<=>?@[\\\]^_`{|}~]*)(\s|$)', re.I)



# This is one regular expression which parses all email addresses out of the text in whatever format they are
email_pattern = re.compile(r"\"?([A-Za-z0-9.'_]+,?[ -]+[A-Za-z0-9'.!]*,?[ &A-Za-z0-9'\.-]*)?\"?[ ]*\"?<?\[?\(?\"?(\w+[.|\w|-]+\w+@[a-zA-Z0-9-]+[.][a-zA-Z][a-zA-Z.-]+|MAILER-DAEMON)?\"?>?\)?\]?\"?[ ]*<?\2?>?;?,? ?")

#Chowan County
#email_pattern = re.compile(r"\"?([A-Za-z0-9.']+,?[ ]+[A-Za-z0-9'.!]*[ &A-Za-z0-9'.-]*\(?\w* ?\w*\)?)?\"?[ ]*\"?<?\[?\(?\"?(\w+[.|\w|-]+\w+@[a-zA-Z0-9-]+[.][a-zA-Z][a-zA-Z.-]+|MAILER-DAEMON)?\"?>?\)?\]?\"?[ ]*<?\2?>?;?,? ?")

# given a string return a list of email addresses in it.
def parse_addresses(string):
    if string == None:
        return []
    line = string[0]
    # First remove all the new line characters
    line= line.replace("\n"," ")
    line= re.sub(r"([ ]+|\t)"," ",line)
    # Remove all the ^M characters from the string
    line = line.replace("\r", "").replace("\n", "")
    #if string is garbage then return empty
    if "DHHS.DSS.County.Directors.Fiscal.Officers" in line:
        return []
    if "=?utf-8" in line:
        return []
    # Now get list of tuples of all name and email matching in the string.
    all_valid_matches = email_pattern.findall(line)
    all_emails =[]
    #print line
    # for each name and email_match you find. If there is no name then name is empty
    for match in all_valid_matches:
        name = match[0]
        email_address=match[1]
        # If no name and email address, means not a valid match and continue to next word
        if len(name)==0 and len(email_address)==0:
            continue
        #print match
        # convert the name to lower case
        name = name.lower()
        present_comma = 0
        # if comma present in name then the order of first name and last name is reversed.
        if "," in name:
            present_comma=1
        name= name.strip()
        # Take only alphnumeric characeters in name
        name = ''.join(e for e in name if e.isalnum() or e==" ")
        name_tuple_string = ""
        # Try to construct email address from name
        if len(name) > 0:
            tokens=  name.split(" ")
            if len(tokens) ==1:
                tokens.append("")
            name_tuple = (tokens[0],tokens[len(tokens)-1])
            name_tuple_string = name_tuple[0] +" "+ name_tuple[1]
            # if there is no email address then only construct email address from name
            if len(email_address)==0 or email_address=="MAILER-DAEMON" :
                if present_comma:
                    # Separate out the first name and last name if there is a comma
                    abs_value = name_tuple[1]
                    second_name = name_tuple[0]
                else:
                    # Separate out the first name and last name if no comma
                    abs_value = name_tuple[0]
                    second_name = name_tuple[1]
                 # Each county has different standards of constructing email address . Based on the standards creeate the new email address
                if email_scan.COUNTY == "Wilkes" or email_scan.COUNTY == "Vance" or email_scan.COUNTY == "Person"or email_scan.COUNTY == "Lincoln" or email_scan.COUNTY == "Lenoir" or email_scan.COUNTY == "Camden" or email_scan.COUNTY == "Caldwell" or email_scan.COUNTY == "Alexander" or email_scan.COUNTY == "Polk" or email_scan.COUNTY == "Montgomery" or email_scan.COUNTY == "Hoke" or email_scan.COUNTY == "Columbus" or email_scan.COUNTY == "Camden":
                    if len(abs_value) > 1:
                        abs_value = abs_value[0]
                    email_address = abs_value + second_name + "@" + email_scan.COUNTY_EXTENSION
                elif email_scan.COUNTY == "Transylvania" or email_scan.COUNTY == "Nash" or email_scan.COUNTY == "McDowell" or email_scan.COUNTY == "Chowan":
                    email_address = abs_value + "." + second_name + "@" + email_scan.COUNTY_EXTENSION
                elif email_scan.COUNTY == "Dare" or email_scan.COUNTY == "Duplin":
                    if len(second_name) > 1:
                        second_name = second_name[0]
                    email_address = abs_value + second_name + "@" + email_scan.COUNTY_EXTENSION
                elif email_scan.COUNTY == "Jackson":
                    email_address = abs_value + second_name + "@" + email_scan.COUNTY_EXTENSION
		elif email_scan.COUNTY == "Randolph" and len(tokens)==3:
                    email_address = tokens[1][0] + tokens[2][0] + tokens[0] + "@" + email_scan.COUNTY_EXTENSION
        email_address = email_address.lower()
        if email_address=="mailer-daemon" or len(email_address)==0:
            continue
        # Now check if the name found was already used before with another email address
        email_address = checkExistingNames(email_address,name_tuple_string) 
        try:
            email_counts[email_address] = email_counts[email_address]+1
        except:
            email_counts[email_address] = 1
        #print email_address
        all_emails.append(email_address)
    return list(set(all_emails))

# In case multiple emailids present per person then try and may them  to one.
def checkExistingNames(email_address,name_tuple_string):
    # now these were some county related observations made while parsing the data and can't be handled by the code. And have been hardcoded here.
    if email_scan.COUNTY == "Jackson":
        if email_address ==  "jacksoncomgr@jacksonnc.org" :
            return "chuckwooten@jacksonnc.org"
    
    if email_scan.COUNTY == "Columbus":
        if email_address ==  "columbus.boe@ncsbe.gov" :
            return "cstrickland@columbusco.org"
                
    if email_scan.COUNTY == "Caldwell":
        if email_address ==  "kmyers@caldwellcountync.org" :
            return "skiser@caldwellcountync.org"   
            
    if email_scan.COUNTY == "Lincoln":
        if email_address ==  "rellis@lincolncounty.org" :
            return "rellis@lincolne911.org"
        if email_address ==  "kelly_atkins@bellsouth.net" :
            return "katkins@lincolncounty.org"

    if email_scan.COUNTY == "Polk":
        if email_address ==  "sghalford@windstream.net" :
            return "sghalford@polknc.org"
    if email_scan.COUNTY == "Duplin":
        if email_address ==  "suzannes@duplincountync.com" :
            return "dcboe@duplincountync.com"
            
    if email_scan.COUNTY == "Hoke":
        if email_address ==  "ctaitt@hokecounty.org" :
            return "hrlc@nc.rr.com"

    if email_scan.COUNTY == "Chowan":
        tokens = email_address.split("@")
        if tokens[1] == "ncmail.net":
            email_address =  tokens[0] +"@" + email_scan.COUNTY_EXTENSION

    if email_scan.COUNTY == "Alexander":
        tokens = email_address.split("@")
        if tokens[1] == "co.alexander.nc.us":
            email_address =  tokens[0] +"@" + email_scan.COUNTY_EXTENSION
    
    if email_scan.COUNTY=="Wilkes":
        tokens = email_address.split("@")
        if "wilkes" in tokens[1]:
            email_address = tokens[0] + "@" + email_scan.COUNTY_EXTENSION
        if email_address == "ghendren@wilkescounty.net":
            return "gregg@wilkescounty.net"
        if email_address == "shamby@wilkescounty.net":
            return "emmgt@wilkescounty.net"
    
    if email_scan.COUNTY=="Vance":
        tokens = email_address.split("@")
        if "vance" in tokens[1]:
            email_address = tokens[0] + "@" + email_scan.COUNTY_EXTENSION
        if email_address == "jayscue@vancecounty.org":
            return "jlayscue@vancecounty.org"

    if email_scan.COUNTY=="Person":
        if email_address == "awehrenberg@personcounty.net":
            return "amyw@personcounty.net"
        if email_address == "agarrett@personcounty.net":
            return "amandag@personcounty.net"
        if email_address == "jhill@personcounty.net":
            return "johnhill@personcounty.net"
    
    if email_scan.COUNTY=="Nash":
        if email_address == "sheriff.all@nashcountync.gov":
            return "dick.jenkins@nashcountync.gov"
    if email_scan.COUNTY=="Montgomery":
        if email_address == "mcsosheriff@montgomerycountync.com":
            return "dempsey.owens@montgomerycountync.com"
        if email_address == "hresources@montgomerycountync.com":
            return "pam.wyatt@montgomerycountync.com"
            
    if email_scan.COUNTY=="McDowell":
        if email_address == "keith.renfro@mcdowellgov.com":
            return "krenfro@mcdowellgov.com"
        if email_address == "cabernathy@mcdowellgov.com":
            return "charlesa@mcdowellgov.com"
    # This is just checks if the given name has already occured before and if it has with what email address. If it exists then get that email address and use the same email address everytime. Otherwise add the current name and email address to the dictionary.
    if len(name_tuple_string)==0:
        return email_address
    tokens = name_tuple_string.split(" ")
    if(len(tokens[1])==0):
        tokens[1] = " "
    try:
        new_email_address = name_mapping[tokens[0]][tokens[1]] 
        return new_email_address
    except:
        pass
    try:
        new_email_address = name_mapping[tokens[1]][tokens[0]] 
        return new_email_address
    except:
        pass
    try:
        name_mapping[tokens[0]][tokens[1]] = email_address
    except:
        name_mapping[tokens[0]] = {}
        name_mapping[tokens[0]][tokens[1]] = email_address
    try:
        name_mapping[tokens[1]][tokens[0]] = email_address
    except:
        name_mapping[tokens[1]] = {}
        name_mapping[tokens[1]][tokens[0]] = email_address
    return email_address

# This is the original code to parse a message and remove the headers and footers from the text message
def parse_message(message):
	# Remove all image tags
	message = str(message)
	if message.count(' ') < 3 and len(message) >25:
	    return ("","")
	#print "Trial1",message
	message = message_re1.sub('', message)
	message = _link.sub('',message)
	#print message
	#print "Trial2",message
	# Split the message on newline boundaries
	lines = message_re2.split(message)
	result = []
	#print "Trial3",lines
	for i in range(len(lines)):
		if lines[i].count(' ') < 3 and len(lines[i]) >30:
	    		continue
		# Look for forward/reply-to delimiters and cut off the message
		if message_re3.match(lines[i]):
			break
		#do not capture information in the reply receipt that will jsut list a bunch of emails.
		if message_re6.match(lines[i]):
			break
		if message_re10.search(lines[i]):
			break
		# Sometimes there are no delimiters except a 
		# On Tuesday ... blah blah
		# From: 
		elif len(lines) > i+1 and message_re4.match(lines[i+1]):
			break
		# Look for lines beginning with >, as they are probably quoted text
		elif not message_re5.match(lines[i]):
			result.append(lines[i])
	# Tokenize'
	#print result
	other_message =  ' '.join(result)
	new_message = message_re8.sub('',other_message)
	new_message = message_re9.sub('',new_message)
	message,extra_info = parse_text(new_message,message=1)
	return (message,extra_info)

# Code to parse text ... remove stopwords and any html tags which exist in the data.
def parse_text(line,message=0):
    extra_info = None
    if "=?" in line:
        return ("","")
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
    if message:
        extra_info = ' '.join(words)
        extra_info = " ".join(extra_info.split())
        extra_info = extra_info.replace("\"","")
    # remove all the special characters.
    words = re.findall(r'[a-zA-Z]+'," ".join(words))
    # this removes all the stopwords 
    new_words = []
    for w in words:
        p = w.lower()
        try:
            a = email_scan.stop_words[p]
        except:
            new_words.append(p)
    line = ' '.join(new_words)
    # convert to string and send it back
    return (line,extra_info)
