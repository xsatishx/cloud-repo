# Samtools Docker Container
FROM healthseq/base

# Maintainer 
MAINTAINER Satish Balakrishnan <satish@healthseq.com>

# Download samtools in /dnasoft and install
RUN wget https://github.com/samtools/samtools/releases/download/1.2/samtools-1.2.tar.bz2 --no-check-certificate &&     
    mv /samtools-1.2.tar.bz2 /dnasoft/samtools-1.2.tar.bz2 &&     
	cd /dnasoft &&     
	tar -xvf /dnasoft/samtools-1.2.tar.bz2 &&     
	cd /dnasoft/samtools-1.2 &&         
	make &&         
	make install &&         
	make prefix=/dnasoft

# Set PATH
ENV PATH /dnasoft/samtools-1.2:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games

# Set working directory for the container
WORKDIR /dnasoft/samtools-1.2/

# Clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/* 
RUN apt-get autoclean && apt-get autoremove -y && rm -rf /var/lib/{apt,dpkg,cache,log}/
RUN rm -rf /dnasoft/samtools-1.2.tar.bz2