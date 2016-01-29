#!/usr/bin/python
import os
import argparse

#import boto
#import boto.s3.connection
#import os
#import re
#import json
#import os.path
#from os.path import basename
#from pprint import pprint

#print("example file: \"ERR_tar.12Mb.gz\"")

# Added some argument parsing so it's easier to wrap this script with others.
parser = argparse.ArgumentParser(description='Script to run Stuti\'s RNASeq processing docker')
parser.add_argument('-f','--list_file', help='list_of_files_to_process (*.fastq.tar.gz, a zip of mate pair fastq files)', required=False, default="filenames_1.txt")
parser.add_argument('-d','--docker_id', help='id of the docker image to use', required=False, default="0ede86ece3ce")
parser.add_argument('-i','--input_dir', help='directory path for input (*.fastq.tar.gz)', required=False, default="/home/ubuntu/SCRATCH/")
parser.add_argument('-o','--output_dir', help='directory path for output', required=False, default="/home/ubuntu/SCRATCH/geuvadis_results/")
args = parser.parse_args()

list_file = args.list_file
docker_id = args.docker_id
output_dir = args.output_dir

#docker_id = "0ede86ece3ce"
#f = open("filenames_1.txt", "r")
f = open(list_file, "r")
#docker_id = docker_id
for filename in f:
    filename = filename.rstrip()
    analysis_id = filename.replace(".fastq.tar.gz", "")
    filepath = output_dir+"/%s" %(filename)
    print "Processing "+analysis_id
    #output = "/home/ubuntu/SCRATCH/geuvadis_results/%s" %(analysis_id)
    output = output_dir+"/%s" %(analysis_id)
    if not os.path.isdir(output):
	os.mkdir(output)

    os.system("docker run -v /home/ubuntu/:/host/home -v /etc:/host/etc -v /mnt/SCRATCH:/home/ubuntu/SCRATCH/ -i -t %s /usr/bin/python /home/ubuntu/expression/pipeline_elastic_cluster_new.py --analysis_id %s --gtf /home/ubuntu/SCRATCH/geuvadis_genome/gencode.v19.annotation.hs37d5_chr.gtf --input_file %s --p 8 --star_pipeline /home/ubuntu/expression/icgc_rnaseq_align/star_align.py --output_dir %s --genome_fasta_file /home/ubuntu/SCRATCH/geuvadis_genome/hs37d5.fa  --genome_dir /home/ubuntu/SCRATCH/geuvadis_genome/star_genome/ --quantMode TranscriptomeSAM --cufflinks_pipeline /home/ubuntu/expression/compute_expression.py --ref_flat /home/ubuntu/SCRATCH/geuvadis_genome/refFlat.txt" %(docker_id, analysis_id, filepath, output))






