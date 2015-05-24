#!/usr/bin/python

####################### Expectation of Code ##########################
# Given the directory which contains all the emails ... This code loops through 
# all the emails parses them and then saves them in a recoverable format 
######################################################################
import sys
import os
import logging
import email_parsing
import pickle
import csv
import text_parsing
import operator



#These are all the dictionaries which are later needed to for easy parsing and printing the output.
# This dictionary maintains a list of unique email ids across all the entire dataset. This dictionary is filled as the code runs and parses mails.
unique_emailids={}
# This dictionary maintains a list of unique emailids across the entire dataset. This dictionary is initialized before mail parsing starts. from the internal mails file.
unique_emailids_internal={}
# Similar to the  unique_emailsids this is a dictionary which maintains unique words across the entire dataset. Filled as emails are parsed
unique_words={}
# Unique tokens for filtered internal emails filled as dataset is parsed.
unique_words_internal={}
# This dictionary is used to check for duplicate emails.
unique_mail_hash={}
# This contains the list of stopwords. Read and intialized before the parsing starts.
stop_words={}
sent_receive_counts={}
internal_mails_data={}
# Use the logger from the previous code.
logger = logging.getLogger(__name__)
all_emails=[]
all_internal_emails=[]
directors_email = []
large_scale = 0
COUNTY = "Randolph"
COUNTY_EXTENSION = ""
spam_classified=0
# Depending on which County is being parsed choose the email extension.
def select_county_extension():
    global COUNTY,COUNTY_EXTENSION,large_scale
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
        large_scale=1
    elif COUNTY == "Camden":
        COUNTY_EXTENSION = "camdencountync.gov"
    elif COUNTY == "Caldwell":
        COUNTY_EXTENSION = "caldwellcountync.org"
    elif COUNTY == "Chowan":
        COUNTY_EXTENSION = "chowan.nc.gov"
    elif COUNTY == "Jackson":
        COUNTY_EXTENSION = "jacksonnc.org"
        large_scale =1
    elif COUNTY == "Alexander":
        COUNTY_EXTENSION = "alexandercountync.gov"
    elif COUNTY == "Polk":
        COUNTY_EXTENSION = "polknc.org"
        large_scale = 1
    elif COUNTY == "Montgomery":
        COUNTY_EXTENSION = "montgomerycountync.com"
    elif COUNTY == "Hoke":
        COUNTY_EXTENSION = "hokecounty.org"
    elif COUNTY == "Duplin":
        COUNTY_EXTENSION = "duplincountync.com"
        # large scale says for huge counties do not generate the edge matrix.
        large_scale = 1
    elif COUNTY == "Columbus":
        COUNTY_EXTENSION = "columbusco.org"
        large_scale=1
    elif COUNTY == "Camden":
        COUNTY_EXTENSION = "camdencountync.gov"
    elif COUNTY == "Randolph":
        COUNTY_EXTENSION = "co.randolph.nc.us"
    else:
        COUNTY_EXTENSION = ""


# Given the stopwords file, output directory and input directory . Start parsing the input directory and generate the necessary output.
def read_emails(directory_name,stopwords_filename,output_directory):
    global COUNTY,COUNTY_EXTENSION
    # The county to be parsed is decided from the name of output directory hence the output directory should be the same name of the county being parsed.
    COUNTY = output_directory[:-1].split("/")[-1]
    print COUNTY
    # Based on the county select the county extension to be appended to the generate emails.
    select_county_extension()
    print COUNTY, COUNTY_EXTENSION
    # Initialize the stopwords dictionary based on the stopwords file provided as input.
    read_stopwords(stopwords_filename)
    # Initialize the unique_emailids_internal dictionary based on the  internal_emails_data file in the output directory
    readListInternalMails(output_directory)
    i=0
    individual_mails=0
    # Now loop through all the email files in the input directory
    for path,subdirs,files in os.walk(directory_name):
        for filename in files:
            f_name = os.path.join(path,filename)
            logger.debug("Processing "+ f_name)
            # definition of valid input files varies in different counties.  Hence based on the counties decide whether the filename is valid or not.	
            if not spam_classified:
		    if (COUNTY == "Polk" or COUNTY == "Hoke" or COUNTY == "Randolph") and filename[-3:] != "eml":
		        logger.debug("Not an email file "+f_name)
		        continue
		    elif COUNTY == "Montgomery" and filename[:2] != "xx":
		        logger.debug("Not an email file "+f_name)
		        continue
		    elif COUNTY == "Duplin" and filename[-4:] != "imap":
		        logger.debug("Not an email file "+f_name)
		        continue
		    elif COUNTY == "Columbus" and filename[-3:] != "MAI":
		        logger.debug("Not an email file "+f_name)
		        continue
		    elif COUNTY != "Polk" and COUNTY != "Montgomery"  and COUNTY != "Hoke" and COUNTY != "Randolph" and COUNTY != "Columbus" and COUNTY!="Duplin" and not filename.isdigit():
		        logger.debug("Not an email file "+f_name)
		        continue
	    else:
	            if not filename.isdigit():
	                logger.debug("Not an email file "+f_name)
	                continue
		    # Avoid the contacts and the Calendar folders
            if "Calendar" in f_name or "Contacts" in f_name:
                logger.debug("Not an email file "+f_name)
                continue
            # Now parse this email.
            parsed_email = email_parsing.parseMail(f_name)
            #Save the filename where the email was parsed.
            parsed_email["file"]= f_name
            # Check if the parsed email is valid email oor not if not then skip that email..
            check = checkParsedEmail(parsed_email)
            if not check:
                continue
            new_to=[]
            from_all = parsed_email["from"][0]
            to_val = ["to"] * len(parsed_email["to"])
            cc_val = ["cc"] * len(parsed_email["cc"])
            all_combined = to_val  + cc_val
            index_no=-1
            cc_info = []
            # Now check whether this email is duplicate or not
            for to_all in parsed_email["to"] + parsed_email["cc"]:
            	index_no = index_no +1
                if from_all == to_all:
                    continue
                # So create the meta string and check if it already exists in unique_mail_hash
                meta_data = from_all + " " + to_all + " " + parsed_email["subject"] + " " + parsed_email["date"]
                try:
                    # If already exists then skip it
                    temp = unique_mail_hash[meta_data]
                    logger.debug("Email already exists " + meta_data)
                    continue
                except:
                    # Else no duplicate hence parse it and add it to the unique_mail_hash
                    unique_mail_hash[meta_data] =1
                individual_mails = individual_mails+1
                new_to.append(to_all)
                cc_info.append(all_combined[index_no])

            if len(new_to) ==0 :
                logger.debug("No valid recipients Found")
                continue
            #Now tokenize the message and subject together and create a list of the string.
            tokens  = (parsed_email["message"]+" "+ parsed_email["subject"]).split(" ")
            new_tokens = []
            for t in tokens:
                a = t.strip()
                if len(a) >= 1:
                    new_tokens.append(a)
            parsed_email["tokens"] = new_tokens
            # Here to is initialized with to and cc
            parsed_email["cc_info"]  = cc_info
            parsed_email["to"] = list(set(new_to))
            # Now based on this email update all the bookkeeping datastructures which later on help to print out the output in necessary format.
        #   print parsed_email["file"]
            #print parsed_email["original_text"]
            #if parsed_email["file"] == "../classified_data/Columbus/ham/11751":
	    #    sys.exit()
	    #print parsed_email["file"]
	    #if "uixebfgtpuquhsaqcaswle" in new_tokens:
	    #	sys.exit()
            updateAllDictionaries(parsed_email)
            all_emails.append(parsed_email)
            i =i +1
    #Output the most popularly used contacts. This is a dictionary hence used outputDictionary     
    outputDictionary(output_directory+"popularity_emails.txt",text_parsing.email_counts) 
    logger.debug("Total number of valid files parsed: "+ str(i))
    logger.debug("Total number of mails: "+ str(individual_mails))
    # Saved the parsed data in a pickle dump
    fp=open(output_directory+"pickle_dump_data.pkl","w")
    pickle.dump(all_emails,fp)
    fp.close()
    # And now generate the work matrix and edge matrix
    outputAllMatrices(output_directory)

# This function initializes unique_emailids_internal based on the department managers emailids provided in internal_emails_data.csv
def readListInternalMails(output_directory):
    fp = open(output_directory+"internal_emails_data.csv","r")
    reader = csv.reader(fp)
    for row in reader:
        header = row
        break
    for row in reader:
        try:
            temp = unique_emailids_internal[row[1]] 
        except:
            unique_emailids_internal[row[1]] =len(unique_emailids_internal )
    	internal_mails_data[row[1]] = [row[0],row[2],row[3]]
    fp.close()

#This function  is to printout the output to the file in the desired format.
def outputAllMatrices(output_directory):
    # Open all the files and csv readers and writers.
    fsummary = open(output_directory+ "summary.csv","w")
    if not spam_classified:
	    fsummary_internal = open(output_directory+ "summary_internal.csv","w")
	    fiwords = open(output_directory+ "word_matrix_internal.csv","w")
	    fiedges = open(output_directory +"edge_matrix_internal.csv","w")
	    fiedges_to = open(output_directory +"edge_matrix_internal_to.csv","w")
	    fiedges_cc = open(output_directory +"edge_matrix_internal_cc.csv","w")
    fwords = open(output_directory +"word_matrix.csv","w")
    fedges = open( output_directory + "edge_matrix.csv","w")
    csummary =csv.writer(fsummary)
    #csummary.writerow(["File","Subject","Text"])
    if not spam_classified:
    	ciedges_to = csv.writer(fiedges_to)
    	ciedges_cc = csv.writer(fiedges_cc)
        csummary_internal = csv.writer(fsummary_internal)
    #csummary_internal.writerow(["File","Subject","Text"])
    # OUtput the list of unique words found
    	ciwords = csv.writer(fiwords)
        all_keys = sorted(unique_words_internal.keys(),key=unique_words_internal.get)
    #ciwords.writerow(["File"] +all_keys)
    	outputList(output_directory+"vocab_internal.txt",all_keys)
    # OUtput the list of unique words found for the whole dataset
    cwords = csv.writer(fwords)
    all_keys = sorted(unique_words.keys(),key=unique_words.get)
    #cwords.writerow(["File"] +all_keys)
    outputList(output_directory+"vocab.txt",all_keys)
    # Output the list of unique emailids for the entire dataset.
    cedges = csv.writer(fedges)
    all_keys = sorted(unique_emailids.keys(),key=unique_emailids.get)
    #cedges.writerow(["File","Index"] +all_keys)
    fauthor = open(output_directory+"authors.txt","w")
    csvauthor = csv.writer(fauthor)
    for i in range(0,len(all_keys)):
    	row = []
    	row.append(all_keys[i])
    	send_r = sent_receive_counts[all_keys[i]]
    	row.append(send_r[0])
    	row.append(send_r[1])
    	internal_data = []
    	try:
    		internal_data = internal_mails_data[all_keys[i]]
    	except:
    		internal_data = ["","",""]
    	csvauthor.writerow(row+internal_data)
    if not spam_classified:
        ciedges = csv.writer(fiedges)
        all_keys = sorted(unique_emailids_internal.keys(),key=unique_emailids_internal.get)
    #ciedges.writerow(["File","Index"] +all_keys)
        outputList(output_directory+"authors_internal.txt",all_keys)
    # For each parsed emails write to the edge and word matrix 
    for email in all_emails:
        # Write down the summary
        row = [ email["file"],email["date"],email["from"][0],email["original_subject"],email["original_text" ]] 
        csummary.writerow(row)
        # if the word matrix for entire dataset is too large then skip it
        if spam_classified:
            # Output to matrices
            row = [0 for i in range(0,len(unique_words))]  
            for token in email["tokens"]:
                row[unique_words[token]] = row[unique_words[token]]+1
            row = [email["file"]]+row 
            cwords.writerow(row)
            row = [0 for i in range(0,len(unique_emailids))]  
            for i in email["to"]:
                row[unique_emailids[i]] = row[unique_emailids[i]]+1
            row = [email["file"], unique_emailids[email["from"][0]] ] +row
            cedges.writerow(row)
        new_emailids=[]
        if not spam_classified:
		# filter out the internal emails 
		try:
		    temp  = unique_emailids_internal[email["from"][0]]
		except:
		    logger.debug("Sender not in authors list "+ email["file"])
		    continue
		cc_emailids=[]
		to_emailids=[]
		index_no =-1
		for emailid in email["to"]:
		    index_no = index_no +1
		    try:
		        temp = unique_emailids_internal[emailid]
		        if email["cc_info"][index_no] == "cc":
		        	cc_emailids.append(emailid)
		        else:
		        	to_emailids.append(emailid)
		        new_emailids.append(emailid)
		    except:
		        continue
		if len(new_emailids)==0:
		    logger.debug("No recipients in authors list "+ email["file"])
		    continue   
		# if valid internal deparment manager email Then output the data to internal word and edge matrices.
		row = [ email["file"],email["date"],email["from"][0], email["original_subject"],email["original_text" ]] 
		csummary_internal.writerow(row)          
		row = [0 for i in range(0,len(unique_words_internal))]  
		for token in email["tokens"]:
		    row[unique_words_internal[token]] = row[unique_words_internal[token]]+1
		row = [email["file"]]+row #+ [email["original_subject"],email["original_text"]]
		ciwords.writerow(row)
		row = [0 for i in range(0,len(unique_emailids_internal))]  
		for i in new_emailids:
		    row[unique_emailids_internal[i]] = row[unique_emailids_internal[i]]+1
		row = [email["file"], unique_emailids_internal[email["from"][0]] ] +row
		ciedges.writerow(row)
		
		row = [0 for i in range(0,len(unique_emailids_internal))]  
		for i in cc_emailids:
		    row[unique_emailids_internal[i]] = row[unique_emailids_internal[i]]+1
		row = [email["file"], unique_emailids_internal[email["from"][0]] ] +row
		ciedges_cc.writerow(row)
		
		row = [0 for i in range(0,len(unique_emailids_internal))]  
		for i in to_emailids:
		    row[unique_emailids_internal[i]] = row[unique_emailids_internal[i]]+1
		row = [email["file"], unique_emailids_internal[email["from"][0]] ] +row
		ciedges_to.writerow(row)
		
    if not spam_classified:
        fsummary_internal.close()
        fiedges.close()
        fiwords.close()
    fwords.close()
    fedges.close()
    fsummary.close()
    fauthor.close()

# Write dictionary to a file # general code
def outputDictionary(filename,dictionary):
    all_keys = sorted(dictionary.items(),key=operator.itemgetter(1),reverse=True) 
    fp = open(filename,"w")
    for key in all_keys:
        fp.write(key[0] + ","+str(key[1])+"\n")
    fp.close()
     
# General code for outputing a list to a file.
def outputList(filename,list_print):
    fp = open(filename,"w")
    for i in list_print:
        fp.write(i+"\n")
    fp.close()
# as the data is parsed uupdate all the data structures for easy output generation
def updateAllDictionaries(parsed_email):
    #accumulate the sender counts
    try:
    	sender_val = sent_receive_counts[parsed_email["from"][0]]
    	sent_receive_counts[parsed_email["from"][0]] = (sender_val[0]+1,sender_val[1])
    except:
    	sent_receive_counts[parsed_email["from"][0]] = (1,0)
    for emailids in parsed_email["to"]:
        try:
    	    sender_val = sent_receive_counts[emailids]
    	    sent_receive_counts[emailids] = (sender_val[0],sender_val[1]+1)
    	except:
    	    sent_receive_counts[emailids] = (0,1)
    all_emailids = [parsed_email["from"][0]] + parsed_email["to"]
    # Update the Uniqueemail ids and words
    updateUniqueEmailids(all_emailids,parsed_email["tokens"])
    # Update the unique internal email ids and words
    updateUniqueEmailidsInternal(parsed_email["from"][0],parsed_email["to"],parsed_email["tokens"])

# function which given a message updates all the unique words for internal emails
def updateUniqueEmailidsInternal(from_all,to_all,message):
    try:
        temp = unique_emailids_internal[from_all]
    except:
        return   
    all_emailids=[] 
    for emailid in to_all:
        try:
            temp = unique_emailids_internal[emailid]
            all_emailids.append(emailid)
        except:
            continue
    if len(all_emailids) ==0:
        return 
    for token in message:
        try:
            temp = unique_words_internal[token]
        except:
            unique_words_internal[token] = len(unique_words_internal)
    
# Function which when given a mail updates all the unique emailids and unique words datastructure for the entire dataset.
def updateUniqueEmailids(all_emailids,total_message):
    for emailid in all_emailids:
        try:
            temp = unique_emailids[emailid]
        except:
            unique_emailids[emailid] = len(unique_emailids)
    for token in total_message:
        try:
            temp = unique_words[token]
        except:
            unique_words[token] = len(unique_words)
        

# Check if a given email is a valid email or not
def checkParsedEmail(parsed_email):
    check =1
    # If valid from is present
    if len(parsed_email["from"]) <1:
        logger.debug("Email doesn't have from clause")
        check =0
    # if valid recipient is present
    if (len(parsed_email["to"]) ==0 and len(parsed_email["cc"])==0):
        logger.debug("Email doesn't have to or cc clause")
        check =0
    # if valid date is present
    if len(parsed_email["date"]) ==0:
        logger.debug("Couldn't find the date")
        check =0
    if "subject" not in parsed_email.keys():
        logger.debug("Couldn't find subject in the email")
        check =0
    if "message" not in parsed_email.keys():
        logger.debug("Couldn't find message in the email")
        check =0
    return check

# Read stopwords 
def read_stopwords(filename):
    filepointer = open(filename,"r")
    while True:
        line = filepointer.readline()
        if not line:
            break
        line = line[:-1]
        stop_words[line]=1
