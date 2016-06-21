# FASTQC TOOL
FROM healthseq/base

# Maintainer 
MAINTAINER Satish Balakrishnan <satish@healthseq.com>

RUN wget -O /dnasoft/fastqc_v0.11.2.zip http://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v0.11.2.zip \
    && unzip /dnasoft/fastqc_v0.11.2.zip -d /dnasoft/ \
    && chmod -R 766 /dnasoft/ \
    && ln -s /dnasoft/FastQC/fastqc /usr/local/bin/fastqc

# set path
ENV PATH /dnasoft/FastQC/jbzip2-0.9.jar:/dnasoft/FastQC/sam-1.103.jar:/dnasoft/FastQC/fastqc:$PATH

# Permissions
RUN chmod -R 777 /dnasoft

#Cleanup the temp dir
RUN rm -rf /dnasoft/fastqc_v0.11.2.zip

# Set the workdir to /dnasoft so that the docker image runs from this path.
WORKDIR /dnasoft/FastQC

#Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* 
RUN apt-get autoclean && apt-get autoremove -y && rm -rf /var/lib/{apt,dpkg,cache,log}/
