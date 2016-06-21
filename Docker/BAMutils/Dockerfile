# Docker container for BamUtils

# Using the HealthSeq Base image
FROM healthseq/base

# Maintainer
MAINTAINER      Satish <satish@healthseq.com>

# Download bamUtils and install it in /dnasoft
RUN wget https://github.com/statgen/bamUtil/archive/master.tar.gz && \
    mv /master.tar.gz /dnasoft/bamutils.tar.gz && \
    cd /dnasoft && \
    tar -xvf /dnasoft/bamutils.tar.gz && \
    cd /dnasoft/bamUtil-master/ && \
        make cloneLib && \
        make  && \
        make install INSTALLDIR=/dnapipeline 


# Set PATH
ENV PATH /dnasoft/bamUtil-master/bin:$PATH

# Set the workdir to /dnasoft 
WORKDIR /dnasoft/bamUtil-master

#Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* && \
    apt-get autoclean && apt-get autoremove -y && rm -rf /var/lib/{apt,dpkg,cache,log}/ && \
    rm -rf /dnasoft/bamutils.tar.gz
