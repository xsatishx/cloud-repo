# pindel TOOL: Dockerfile

FROM debian:jessie

# Maintainer 
MAINTAINER Satish Balakrishnan <satish@healthseq.com>

# Set correct environment variables.
ENV HOME /root
ENV DEBIAN_FRONTEND noninteractive

# Update
RUN apt-get update -y && apt-get upgrade -y && apt-get install wget unzip perl bioperl build-essential libffi-dev libxml2-dev libxslt1-dev python-dev openjdk-7-jdk openjdk-7-doc openjdk-7-jre-lib -y


#set java
ENV JAVA_HOME /usr/lib/jvm/java-7-openjdk-amd64/jre/bin/java
RUN sed -i 'aPATH=$PATH:/usr/lib/jvm/java-7-openjdk-amd64/jre/bin' /root/.bashrc
RUN mkdir /dnasoft && \
    cd /dnasoft && \
	git clone --branch=develop git://github.com/samtools/htslib.git && \
    git clone --branch=develop git://github.com/samtools/bcftools.git && \
    git clone --branch=develop git://github.com/samtools/samtools.git && \
	cd /dnasoft/htslib && \
	autoconf && \
    ./configure  && \
    make && \
    make install && \
	
	cd /dnasoft && \
	cd /dnasoft/bcftools && \
    make && \
    make install && \
	
	cd /dnasoft && \
	wget -O /dnasoft/samtools-1.2.tar.bz2 https://github.com/samtools/samtools/releases/download/1.2/samtools-1.2.tar.bz2 && \
	tar -xvf /dnasoft/samtools-1.2.tar.bz2 && \
    cd /dnasoft/samtools-1.2 && \
        make && \
        make install && \
        make prefix=/dnapipeline && \
	
    cd /dnasoft/ && \
	git clone git://github.com/genome/pindel.git && \
	chmod -R 777 ./pindel && \
	cd pindel && \
	/bin/sh ./INSTALL /dnasoft/samtools-1.2 && \
    chmod -R 777 /dnasoft/pindel && \
    cp -puv Adaptor.pm bam2pindel.pl pindel pindel2vcf sam2pindel /usr/local/bin/


# set path
ENV PATH /dnasoft/samtools-1.2:/dnasoft/pindel:$PATH

# Permissions
RUN chmod -R 777 /dnasoft

#Cleanup the temp dir
RUN rm -rf /dnasoft/samtools-1.2.tar.bz2

#open ports private only
EXPOSE 8080

# set cmd
CMD ["/bin/bash"]

#Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* 
RUN apt-get autoclean && apt-get autoremove -y && rm -rf /var/lib/{apt,dpkg,cache,log}/
