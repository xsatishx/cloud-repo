#------------------------------------------------#
# FASTQC TOOL: Dockerfile
#------------------------------------------------#
# ENV PATH /dnasoft/Platypus_0.8.1/:$PATH
# Base im
FROM debian:jessie

# Maintainer 
MAINTAINER Stephen Newhouse stephen.j.newhouse@gmail.com

# Set correct environment variables.
ENV HOME /root
ENV DEBIAN_FRONTEND noninteractive

# Update
RUN apt-get update -y && apt-get upgrade -y && apt-get install wget unzip perl bioperl build-essential -y
RUN apt-get install -y openjdk-7-jdk openjdk-7-doc openjdk-7-jre-lib

#set java
ENV JAVA_HOME /usr/lib/jvm/java-7-openjdk-amd64/jre/bin/java
RUN sed -i 'aPATH=$PATH:/usr/lib/jvm/java-7-openjdk-amd64/jre/bin' /root/.bashrc
#-------------------------NGS-TOOL---------------------------------------
# + FastQC
    RUN mkdir /dnasoft \
        && wget -O /dnasoft/fastqc_v0.11.2.zip http://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v0.11.2.zip \
        && unzip /dnasoft/fastqc_v0.11.2.zip -d /dnasoft/ \
        && chmod -R 766 /dnasoft/ \
      
        && ln -s /dnasoft/FastQC/fastqc /usr/local/bin/fastqc

ENV PATH /dnasoft/FastQC/jbzip2-0.9.jar:/dnasoft/FastQC/sam-1.103.jar:/dnasoft/FastQC/fastqc:$PATH
#-------------------------------PERMISSIONS--------------------------
RUN chmod -R 777 /dnasoft

#---------------------------------------------------------------------
#Cleanup the temp dir
RUN rm -rf /dnasoft/fastqc_v0.11.2.zip

#open ports private only
EXPOSE 8080

# Use baseimage-docker's bash.
CMD ["/bin/bash"]

#Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* 
RUN apt-get autoclean && apt-get autoremove -y && rm -rf /var/lib/{apt,dpkg,cache,log}/
