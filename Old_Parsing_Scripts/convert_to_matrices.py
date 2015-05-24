#!/usr/bin/python

import sys
import os
import re
import pickle

vocab = {}
	
#original version reads from a file that goes something like 3 sheila.cozart@transylvaniacounty.org 1340 22 that is just populated with lines output by the identify_addresses.py script. 
#def read_address_list(authors_file):
	#return map(lambda x: x.split()[1].strip().lower(), open(authors_file).readlines())

#This version will just take plain email addresses 1 per line assuming they are already nicely formatted as : sheila.cozart@transylvaniacounty.org on each line
def read_address_list(authors_file):
	return map(lambda x: x.strip().lower(), open(authors_file).readlines())

def filter_email(email, address_list):
	email['from'] = filter_addresses(email['from'], address_list)
	email['to'] = filter_addresses(email['to'], address_list)
	email['cc'] = filter_addresses(email['cc'], address_list)

	# IF email['from'][0] in email['to'] or email['cc'] remove it!

	if email['from']:
		addr = email['from'][0]

		# Remove "From" address from "To" and "CC"
		email['to'] = filter(lambda x: x != addr, email['to'])
		email['cc'] = filter(lambda x: x != addr, email['cc'])

	if email['from'] and (email['to'] or email['cc']):
		message = email['subject'] + '\n\n' + email['message']
		tokens = message.split()
		email['tokens'] = map(map_token, tokens)

		#if re.search('sent', email['file']) and not re.search('presentations', email['file']):  #commented out because we do not have a clean message structure so only looking at the sent folder will exclude all emails
		return email

	return

def filter_addresses(addresses, address_list):
	return filter(lambda x: x in address_list, map(lambda x: x.lower(), addresses))

def map_token(token):
	if token not in vocab:
		vocab[token] = len(vocab)
	
	return vocab[token]

if __name__ == '__main__':
	if len(sys.argv) < 4:
		print >> sys.stderr, "Usage: " + sys.argv[0] + " pickle_file authors_file OUT_DIR"
		sys.exit()

	pickle_file = sys.argv[1]
	authors_file = sys.argv[2]
	OUT_DIR = sys.argv[3]

	if not os.path.isdir(OUT_DIR):
		print >> sys.stderr, OUT_DIR + " is not a directory"
		sys.exit()

	address_list = read_address_list(authors_file)
	print address_list
	
	emails = pickle.load(open(pickle_file))
	
	print "Processing emails..."
	messages = []
	for email in emails:
		email = filter_email(email, address_list)
		if email != None:
			messages.append(email)

	print len(messages), "messages"
	
	print "Writing output files..."
	
	vocab_file = open(os.path.join(OUT_DIR, 'vocab.txt'), 'w')
	# Sort vocabulary by index number
	vocab = sorted(vocab.keys(), key=vocab.get)
	vocab_file.write('\n'.join(vocab))
	vocab_file.close()
	
	word_file = open(os.path.join(OUT_DIR, 'word-matrix.csv'), 'w')
	connections_file = open(os.path.join(OUT_DIR, 'edge-matrix.csv'), 'w')

	summary_file = open(os.path.join(OUT_DIR, 'summary-matrices.tab'), 'w') #changed so that it would not conflict with summary from corpus out file
	summary_file.write("File\tFrom\tToCC\tDate\tSubject\tTokens\n")

	for email in messages:
		summary_file.write('{0}\t{1}\t{2}\t{3}\t{4}\t{5}\n'.format(email['file'], email['from'][0], len(email['to']) + len(email['cc']), email['date'], email['subject'], len(email['tokens'])))

		tokens = email['tokens']
		word_file.write(email['file'])
		for word in range(len(vocab)):
			count = len(filter(lambda x: x == word, tokens))
			word_file.write(',' + str(count))
		word_file.write('\n')
	
		connections_file.write(email['file'])
		connections_file.write(',' + str(address_list.index(email['from'][0])))
		for address in address_list:
			if address in email['to'] or address in email['cc']:
				connections_file.write(',1')
			else:
				connections_file.write(',0')
		connections_file.write('\n')
	
	print "Done!"
	
	summary_file.close()
	word_file.close()
	connections_file.close()

