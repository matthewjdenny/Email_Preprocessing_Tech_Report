#!usr/bin/python

############################## Code Expectation #####################################
# The code takes as input a single file representing the email and separates the 
# various components after doing all the required preprocessing.
######################################################################################

import text_parsing
import sys
import email.parser
import email.utils
import logging
import datetime
import re

# Use the logger created in the parent call to write down all the observed things out here.
logger = logging.getLogger(__name__)
parser = email.parser.Parser()

def parseMail(filename):
    return_type={}
    # Open the file for parsing.
    email = parser.parse(open(filename,"r"))
    # Get string containing the sender section of email.
    from_email = obtainFromEmail(email)
    # Parse the string sender section to get an email_address. The is in the form of a list.
    return_type["from"] = text_parsing.parse_addresses(from_email)
    # Similary obtain the string which is in the "To" section of email.
    to_email = obtainToEmail(email)
    # Get a list of parsed email ids from this parsed section.
    return_type["to"] = text_parsing.parse_addresses(to_email)
    # Get the string representation of the cc section.
    cc_email = obtainCcEmail(email)
    # Convert it to list of parsed email ids.
    return_type["cc"] = text_parsing.parse_addresses(cc_email)
    # Obtain the date the email was sent.
    date = obtainDateEmail(email)
    if date!=None:
    	comma = date[0].split(",")
    	if len(comma) ==2:
    		comma = comma[1].strip()
    	else:
    		comma = comma[0].strip()
    	# If there is a valid date then note it down
    	provided_date = comma.split(" ")
    	if len(provided_date)>1 and len(provided_date[1]) == 1:
    		provided_date[1] = "0" +provided_date[1]
    	add_subtract = 1
    	if len(provided_date)>4 and len(provided_date[4])>4 and provided_date[4][0] == "-":
    		add_subtract = -1
    	try:
	    	timezone_hours = int(provided_date[4][1:3])
	    	timezone_minutes = int(provided_date[4][3:5])
	except:
		timezone_hours = 0
		timezone_minutes = 0
    	provided_date = " ".join(provided_date[0:4])
    	try:
	    	datetime_object= datetime.datetime.strptime(provided_date,"%d %b %Y %H:%M:%S")
	    	new_date_utc = datetime_object + add_subtract* datetime.timedelta(hours = timezone_hours, minutes = timezone_minutes)
		print_date = new_date_utc.strftime("%d %b %Y %H:%M:%S")
		return_type["date"] = print_date
        except:
		logger.debug("Could not find date in the correct format. Skipping it " + date[0])
		return_type["date"] = ""
    else:
    	# Else no valid date
        return_type["date"] = ""
    # Now obtain the subject section of the email.
    subject = obtainSubjectEmail(email)
    if subject!=None:
    	#If there is a valid subject
    	# save the original subject for printing it as raw text
        return_type["original_subject"] = subject[0]
        # This parses the subject and removes all the stopwords and everything. to give cleaner tokenized subject
        subject,extra_info = text_parsing.parse_text(subject[0])
        return_type["subject"] = subject.replace("\"","")
    # Finally obtain the text section of the email.
    message = obtainMessageEmail(email)
    if message  == None:
        return return_type
    # Parse this email text and remove the headers and footers, stopwords, and cleaned and tokenized.
    message,original_text = text_parsing.parse_message(message)
    return_type["message"] = message
    return_type["original_text"] = original_text
    # Return the email object.
    return return_type

# Function to extract from section of email
def obtainFromEmail(email):
    return email.get_all("From")

# Function to extract to section of email.
def obtainToEmail(email):
    return email.get_all("To")

# Function to extract cc section of email.
def obtainCcEmail(email):
    return email.get_all("Cc")

# Function to extract bcc section of email.
def obtainBccEmail(email):
    return email.get_all("Bcc")

# Function to extract date section of email.
def obtainDateEmail(email):
    date = email.get_all("date")
    return date

# Function to extract subject section of email.
def obtainSubjectEmail(email):
    return email.get_all("subject")

# function to extract text section of email.
def obtainMessageEmail(email):
    while True:
        try:
            email = email.get_payload(0)
        except:
            break
    email = email.get_payload()
    return email
