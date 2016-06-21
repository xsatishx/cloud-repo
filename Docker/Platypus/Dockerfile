# Platypus TOOL
FROM healthseq/base

# Maintainer 
MAINTAINER Satish Balakrishnan <satish@healthseq.com>

# Download and Installation
RUN wget http://www.well.ox.ac.uk/bioinformatics/Software/Platypus-latest.tgz && \
    mv /Platypus-latest.tgz /dnasoft/Platypus-latest.tgz && \
    cd /dnasoft && \
    tar -xvf /dnasoft/Platypus-latest.tgz && \
    cd /dnasoft/Platypus_0.8.1 && \
    ./buildPlatypus.sh 

# Set PATH
ENV PATH /dnasoft/Platypus_0.8.1/:$PATH

# Finally, set the workdir to /dnasoft so that the docker image runs from this path.
WORKDIR /dnasoft

# Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* 
RUN apt-get autoclean && apt-get autoremove -y && rm -rf /var/lib/{apt,dpkg,cache,log}/
RUN rm -rf /dnasoft/Platypus-latest.tgz && \
    rm -rf /dnasoft/SwiftSeq_local_test_v2.tar && \
    rm -rf /dnasoft/bwa-0.7.12.tar.bz2 && \
    rm -rf /dnasoft/htslib-1.3.tar.bz2 && \
    rm -rf /dnasoft/samtools-1.2.tar.bz2 && \
    rm -rf /dnasoft/picard.tar.gz && \
    rm -rf /dnasoft/bamutils.tar.gz