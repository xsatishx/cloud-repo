# Dockerfile for Bowtie
FROM healthseq/base

# Maintainer
MAINTAINER      Satish <satish@healthseq.com>

# Installation
RUN cd /dnasoft && \
    wget https://sourceforge.net/projects/bowtie-bio/files/bowtie2/2.2.7/bowtie2-2.2.7-linux-x86_64.zip && \
    cd /dnasoft && \
    unzip bowtie2-2.2.7-linux-x86_64.zip  
	
# Set PATH
ENV PATH /dnasoft/bowtie2-2.2.7:$PATH
ENV BT2_HOME=/dnasoft/bowtie2-2.2.7

# Set the workdir to /dnasoft so that the docker image runs from this path.
WORKDIR /dnasoft/bowtie2-2.2.7

#Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/*  && \
    apt-get autoclean && apt-get autoremove -y && rm -rf /var/lib/{apt,dpkg,cache,log}/

