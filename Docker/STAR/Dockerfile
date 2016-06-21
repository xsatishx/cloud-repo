# Dockerfile for STAR
FROM healthseq/base

# Maintainer 
MAINTAINER Satish Balakrishnan <satish@healthseq.com>

# Download the software in /dnasoft
RUN cd /dnasoft && \
    wget https://github.com/alexdobin/STAR/archive/2.5.1b.tar.gz && \
	tar -xvf 2.5.1b.tar.gz && \
	cd /dnasoft/STAR-2.5.1b/ && \
	make 

# Set PATH
ENV PATH /dnasoft/STAR-1.5.1b/bin:$PATH

# Set working directory for the container
WORKDIR /dnasoft/STAR-1.5.1b/

# clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/* 
RUN apt-get autoclean && apt-get autoremove -y && rm -rf /var/lib/{apt,dpkg,cache,log}/
RUN rm -rf /dnasoft/2.5.1b.tar.gz
	
   
    
