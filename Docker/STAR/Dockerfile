# Dockerfile for STAR

FROM ubuntu:12.04

#Maintainer
MAINTAINER      Satish <satish@healthseq.com>

# TODO - Change cd to WORKDIR
ENV JAVA_VERSION=8

# Install necessary packages including java 8 jre and clean up apt caches
RUN echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" >> /etc/apt/sources.list.d/webupd8team-java.list && \
    echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" >> /etc/apt/sources.list.d/webupd8team-java.list && \
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys EEA14886 && \
    echo debconf shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections && \
    echo debconf shared/accepted-oracle-license-v1-1 seen true | /usr/bin/debconf-set-selections && \

    apt-get update && apt-get --no-install-recommends install -y --force-yes \
    oracle-java${JAVA_VERSION}-installer && \ 
    apt-get clean autoclean && \
    apt-get autoremove -y && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/ /var/cache/oracle-jdk${JAVA_VERSION}-installer  && \
# Install packages required by python , gcc, make , wget etc
    apt-get install ant libncurses-dev build-essential make wget zlib1g-dev git g++ gcc -y 

	
# Download the software in /dnasoft
RUN mkdir /dnasoft && \
    cd /dnasoft && \
    wget https://github.com/alexdobin/STAR/archive/2.5.1b.tar.gz && \
	tar -xvf 2.5.1b.tar.gz && \
	cd /dnasoft/STAR-2.5.1b/ && \
	make 

# Set PATH
ENV PATH /dnasoft/STAR-1.5.1b/bin:$PATH

# clean up
RUN rm -rf /dnasoft/2.5.1b.tar.gz
	
   
    
