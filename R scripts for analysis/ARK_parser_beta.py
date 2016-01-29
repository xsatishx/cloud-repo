#!/usr/bin/python

# 11-6-15 This is a simple script to parse Mark's ARKs to get  the URLs
# updated 12-9-15, 12-10-15
#### ARK Parser

# load packages etc.
import argparse
import json
import os.path
import os
import re
import sys
from os.path import basename
from pprint import pprint

# define functions
def find_between(S, begin_str, end_str):
	return (S.split(begin_str))[1].split(end_str)[0]

# parse input arguments
#if help:
#    print "\n" + os.path.basename(sys.argv[0] + " : A tool to extract ftp or S3 URLs from CDIS ARKs")
#    print "\nexample ark: \"http://192.170.232.74:8080/alias/ark:/31807/DC0-25a0b68b-12d0-47ea-b7eb-03bc5fc832b6\"\n"
    
# usage = "usage: %prog [options] arg1 arg2"
parser = argparse.ArgumentParser("ARK_parser.py")
parser.add_argument("-a", "--ark", help="ARK id to parse")
parser.add_argument("-s", "--store_type", help="Store type you want returned, \"ftp\" or \"s3\" URL", default="ftp")
parser.add_argument("-e", "--example", action="store_true", help="Show an example ARKid to query")
parser.add_argument("-d", "--debug", action="store_true", help="Run this script in debug mode")
args = parser.parse_args()

# provide example ARK for easy testing
if args.example:
    print "\nexample ark: \"http://192.170.232.74:8080/alias/ark:/31807/DC0-25a0b68b-12d0-47ea-b7eb-03bc5fc832b6\""
    sys.exit()

if not args.ark:
    print "You must provide an ARK id to parse\nTry \"ARK_parser_beta.py -e\" to see an example ARKid"
    sys.exit()

# exit with error if store type is not an acceptable value
if args.store_type == "ftp":
    if args.debug:
        print "store_type", args.store_type
elif args.store_type == "s3":
    if args.debug:
        print "store_type", args.store_type
else:
    print "\t( "+ args.store_type + " )" + " is not an acceptable value for store_type.\n\tIt Must be \"ftp\" or \"S3\""
    exit()

if args.debug:
    print "ark       ", args.ark

## # enter the ark
## example_ark = input('Enter your ARK Address (surounded by quotes): ')

## # select_source
## my_source = input('Enter your source ("s3" or "ftp"): ')

# get the ark basename
ark_basename = basename(args.ark).rstrip()

# create a string to perform the download
download_string = "curl -s " + args.ark + " -o " + ark_basename
if args.debug:
    if args.debug:
        print "DOWNLOAD STRING " + download_string

# make a system call to download the file -- it will be named for the the last portion in the ark path = basename
# the file will be a json object
os.system(download_string)

# print the contents of the file (in a bit of a wonky way using a system call)
print_string = "less " + ark_basename + " | python -mjson.tool"
if args.debug:
    os.system(print_string)

# import the ark json from file
with open(ark_basename) as data_file:    
    ark_json = json.load(data_file)
    #pprint(ark_json)

# get the URLS
ark_urls = ark_json["urls"]
# u' just indicates that it is unicode
# print mail_accounts[0]["i"]
    
# Print the requested url (if it is there)
for x in ark_urls:
    if args.debug:
        print x        
    if args.store_type=="ftp":
        if x.startswith("ftp://"):
            print x
    elif args.store_type=="s3":
        if x.startswith("s3://"):
            print x
    else:
        print("Invalid store_type selection")



        
# string searches


        
