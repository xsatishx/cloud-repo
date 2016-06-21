# Base Image for HealthSeq
FROM debian:jessie

# Maintainer
MAINTAINER      Satish <satish@healthseq.com>

ENV JAVA_VERSION=8

# Install necessary packages including java 8
RUN echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" >> /etc/apt/sources.list.d/webupd8team-java.list && \
    echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" >> /etc/apt/sources.list.d/webupd8team-java.list && \
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys EEA14886 && \
    echo debconf shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections && \
    echo debconf shared/accepted-oracle-license-v1-1 seen true | /usr/bin/debconf-set-selections && \
    apt-get update && apt-get --no-install-recommends install -y --force-yes\
    oracle-java${JAVA_VERSION}-installer && \
    apt-get install --no-install-recommends unzip ca-certificates python-dev libncurses-dev build-essential make wget libc6 libc-dev git cpp gcc mono-mcs zlib1g-dev libxml2-dev libxslt-dev libxslt1-dev  -y --fix-missing && \

# Clean up
    rm -rf /var/lib/{apt,dpkg,cache,log}/ /var/cache/oracle-jdk${JAVA_VERSION}-installer  && \
    apt-get clean autoclean  && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get autoremove -y && \

# Create workdir
    mkdir /dnasoft
	
