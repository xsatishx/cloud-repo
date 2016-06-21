# Dockerfile for BWA
FROM healthseq/base

# Maintainer
MAINTAINER      Satish <satish@healthseq.com>

# Installation
RUN wget http://sourceforge.net/projects/bio-bwa/files/bwa-0.7.12.tar.bz2 && \
    mv /bwa-0.7.12.tar.bz2 /dnasoft/bwa-0.7.12.tar.bz2 && \
    cd /dnasoft && \
    tar -xvf /dnasoft/bwa-0.7.12.tar.bz2 && \
    cd /dnasoft/bwa-0.7.12 && \
    make

# Set Path
ENV PATH /dnasoft/bwa-0.7.12:$PATH

# Set the workdir to /dnasoft so that the docker image runs from this path.
WORKDIR /dnasoft/bwa-0.7.12

#Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* 
RUN apt-get autoclean && apt-get autoremove -y && rm -rf /var/lib/{apt,dpkg,cache,log}/
