# Picard TOOL
FROM healthseq/base

# Maintainer 
MAINTAINER Satish Balakrishnan <satish@healthseq.com>

# Download and install Picard
RUN wget https://s3.amazonaws.com/data-upload-satish/picard.tar.gz && \
    mv /picard.tar.gz /dnasoft/picard.tar.gz && \
    cd /dnasoft && \
    tar -xvf /dnasoft/picard.tar.gz && \
    cd /dnasoft/broadinstitute-picard-3a81eb1/ && \
    git config --global http.sslVerify false && git clone https://github.com/samtools/htsjdk.git && \
    ant clean all && \
    mv dist/picard.jar picard.jar && \
    mv src/scripts/picard/docker_helper.sh docker_helper.sh && \
    ant clean && \
    rm -rf htsjdk && \
    rm -rf src && \
    rm -rf lib && \
    rm build.xml
    
# Set PATH
ENV PATH /dnasoft/broadinstitute-picard-3a81eb1:$PATH

# Permissions
RUN chmod a+x /dnasoft/broadinstitute-picard-3a81eb1/picard.jar

# Finally, set the workdir to /dnasoft so that the docker image runs from this path.
WORKDIR /dnasoft

#Clean up APT when done.
RUN rm -rf /dnasoft/picard.tar.gz 
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN apt-get autoclean && apt-get autoremove -y && rm -rf /var/lib/{apt,dpkg,cache,log}/