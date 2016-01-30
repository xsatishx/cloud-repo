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
    apt-get install ant python-dev libncurses-dev build-essential make wget libc6 libc-dev git cpp gcc mono-mcs zlib1g-dev libxml2-dev libxslt-dev libxslt1-dev python-dateutil python-docutils python-feedparser python-gdata python-jinja2 python-ldap python-libxslt1 python-lxml python-mako python-mock python-openid python-psycopg2 python-psutil python-pybabel python-pychart python-pydot python-pyparsing python-reportlab python-simplejson python-tz python-unittest2 python-vatnumber python-vobject python-webdav python-werkzeug python-xlwt python-yaml python-zsi -y 

# Download Picard
RUN wget https://s3.amazonaws.com/data-upload-satish/picard.tar.gz && \
    
# make a dnasoft directory to move all the downloaded files
    mkdir /dnasoft && \
    mv /picard.tar.gz /dnasoft/picard.tar.gz && \
    
# untar the gz files inside dnasoft
 cd /dnasoft && \
 tar -xvf /dnasoft/picard.tar.gz && \
 
# Installation of all the tools as per standary documentation
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
  
# Clean Up

RUN rm -rf /dnasoft/picard.tar.gz 
    
# Set PATH
ENV PATH /dnasoft/broadinstitute-picard-3a81eb1:$PATH

# Permissions
RUN chmod a+x /dnasoft/broadinstitute-picard-3a81eb1/picard.jar

# Finally, set the workdir to /dnasoft so that the docker image runs from this path.
WORKDIR /dnasoft
