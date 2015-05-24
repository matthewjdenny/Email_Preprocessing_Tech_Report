#!usr/bin/python

############### Expected behaviour of code ##################################
# The code expects three types of input
# ---- directory name .. directory name which contains all the input files converted to text.
#----- stopwords filename ... Filename containing stopwords.
#----- Output directory ..... Where to store the output in . The output directory name should be same as the county you want to parse with the first letter capital and internal_emails_data.csv should be present in this folder for the code to run
#############################################################################

import sys
import email_scan
import logging
import time
import os



def check_integrity_file(filename):
    if not os.path.isfile(filename):
        print filename + "file does not exist"
        logging.debug(filename + "file does not exist")
        sys.exit()


def check_integrity_directory(directory_name):
    if not os.path.isdir(directory_name):
        print directory_name + "directory does not exist"
        logging.debug(directory_name + "directory does not exist")
        sys.exit()


if __name__ == '__main__':
    if len(sys.argv)<4:
        print "Expected Arguments"
        print "2. python run.py directory_name stopwords_filename output_directory"
        sys.exit()
    if len(sys.argv) == 4:
        check_integrity_directory(sys.argv[1])
        check_integrity_file(sys.argv[2])
        directory_name = sys.argv[1]
        stopwords_filename = sys.argv[2]
        output_filename= sys.argv[3].rstrip("/") + "/"
        LOG_FILENAME = "logger" + time.strftime("%m_%d_%Y_%H_%M_%S") + ".log"
        logging.basicConfig(filename = output_filename +LOG_FILENAME,level=logging.DEBUG)
        logging.debug("Start scanning and parsing emails")
        email_scan.read_emails(directory_name,stopwords_filename,output_filename)
