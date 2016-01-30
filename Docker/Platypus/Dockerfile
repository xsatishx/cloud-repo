# Dockerfile for platypus

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
    apt-get clean autoclean && apt-get autoremove -y && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/ /var/cache/oracle-jdk${JAVA_VERSION}-installer  && \
# Install packages required by python , gcc, make , wget etc
    apt-get install ant python-dev libncurses-dev build-essential make wget libc6 libc-dev git cpp gcc mono-mcs zlib1g-dev libxml2-dev libxslt-dev libxslt1-dev python-dateutil python-docutils python-feedparser python-gdata python-jinja2 python-ldap python-libxslt1 python-lxml python-mako python-mock python-openid python-psycopg2 python-psutil python-pybabel python-pychart python-pydot python-pyparsing python-reportlab python-simplejson python-tz python-unittest2 python-vatnumber python-vobject python-webdav python-werkzeug python-xlwt python-yaml python-zsi -y 

# Download the tools - All wget should go here
RUN wget http://www.well.ox.ac.uk/bioinformatics/Software/Platypus-latest.tgz && \

# make a dnasoft directory to move all the downloaded files
    mkdir /dnasoft && \
    mv /Platypus-latest.tgz /dnasoft/Platypus-latest.tgz && \
    
# untar the gz files inside dnasoft
   cd /dnasoft && \
      tar -xvf /dnasoft/Platypus-latest.tgz && \
 
# Installation of all the tools as per standary documentation
   cd /dnasoft/Platypus_0.8.1 && \
     ./buildPlatypus.sh 

# Clean Up

RUN rm -rf /dnasoft/Platypus-latest.tgz && \
    rm -rf /dnasoft/SwiftSeq_local_test_v2.tar && \
    rm -rf /dnasoft/bwa-0.7.12.tar.bz2 && \
    rm -rf /dnasoft/htslib-1.3.tar.bz2 && \
    rm -rf /dnasoft/samtools-1.2.tar.bz2 && \
    rm -rf /dnasoft/picard.tar.gz && \
    rm -rf /dnasoft/bamutils.tar.gz

	# Set PATH
ENV PATH /dnasoft/Platypus_0.8.1/:$PATH
# Finally, set the workdir to /dnasoft so that the docker image runs from this path.
WORKDIR /dnasoft
