# Picard	 Dockerfile

FROM debian:jessie

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
apt-get install unzip ant python-dev libncurses-dev build-essential make wget libc6 libc-dev git cpp gcc -y 

RUN mkdir /dnasoft && \
    cd /dnasoft && \
    wget https://sourceforge.net/projects/bowtie-bio/files/bowtie2/2.2.7/bowtie2-2.2.7-linux-x86_64.zip && \
    cd /dnasoft && \
    unzip bowtie2-2.2.7-linux-x86_64.zip  
# Set PATH
ENV PATH /dnasoft/bowtie2-2.2.7:$PATH
ENV BT2_HOME=/dnasoft/bowtie2-2.2.7
# Permissions

# Finally, set the workdir to /dnasoft so that the docker image runs from this path.
WORKDIR /dnasoft
