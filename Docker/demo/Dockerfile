# Installs BWA and does a bwa index with a trimmed human_g1k_v37 sequence - For Demo Only
FROM ubuntu:14.04
MAINTAINER      Satish <satish@healthseq.com>
RUN apt-get update && \
    apt-get -y install gcc mono-mcs zlib1g-dev make wget git -y -f && \


wget http://sourceforge.net/projects/bio-bwa/files/bwa-0.7.12.tar.bz2 && \
mkdir /dnasoft && \
mv /bwa-0.7.12.tar.bz2 /dnasoft/bwa-0.7.12.tar.bz2 && \
cd /dnasoft && \
tar -xvf /dnasoft/bwa-0.7.12.tar.bz2 && \
cd /dnasoft/bwa-0.7.12 && \
make 


ENV             PATH /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/opt/bin:/dnasoft/bwa-0.7.12
#cd /dnasoft && \
#wget https://s3.amazonaws.com/data-upload-satish/human_g1k_v37_trimmed.fasta.gz && \
#gunzip human_g1k_v37_trimmed.fasta.gz && \

#cd /dnasoft/bwa-0.7.12 && \
#./bwa index /dnasoft/human_g1k_v37_trimmed.fasta


