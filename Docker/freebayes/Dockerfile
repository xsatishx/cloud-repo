FROM debian:jessie

# Maintainer
MAINTAINER Satish Balakrishnan <satish@healthseq.com>

# Set environment variables.
ENV HOME /root
ENV DEBIAN_FRONTEND noninteractive

# Update
RUN apt-get update -y && apt-get upgrade -y && apt-get install wget unzip build-essential libffi-dev libxml2-dev libxslt1-dev python-dev openjdk-7-jdk openjdk-7-doc openjdk-7-jre-lib git automake cmake make zlib1g-dev ncurses-dev -y

#set java
ENV JAVA_HOME /usr/lib/jvm/java-7-openjdk-amd64/jre/bin/java
RUN sed -i 'aPATH=$PATH:/usr/lib/jvm/java-7-openjdk-amd64/jre/bin' /root/.bashrc
RUN mkdir /dnasoft 

# install freebayes
RUN cd /dnasoft \
  && git clone --recursive git://github.com/ekg/freebayes.git \
  && cd /dnasoft/freebayes \
  && make \
  && chmod -R 777 /dnasoft/freebayes \
  && cp -v /dnasoft/freebayes/bin/* /usr/local/bin

# Permissions
RUN chmod -R 777 /dnasoft

# Cleanup the temp dir
RUN rm -rf /tmp/*

# Set Path
ENV PATH /dnasoft/freebayes/bin:$PATH

#Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN apt-get autoclean && apt-get autoremove -y && rm -rf /var/lib/{apt,dpkg,cache,log}/





