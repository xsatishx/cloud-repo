FROM debian:jessie
MAINTAINER      Satish <balakrishnan.satish@gmail.com>

# TODO - Clean all setupfiles to reduce the image size
# TODO - Mention where the executables are available - the path
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
    rm -rf /var/lib/{apt,dpkg,cache,log}/ /var/cache/oracle-jdk${JAVA_VERSION}-installer && \

# Install packages required by python , gcc, make , wget etc
apt-get install ant python-dev libncurses-dev build-essential make wget libc6 libc-dev git cpp gcc mono-mcs zlib1g-dev libxml2-dev libxslt-dev libxslt1-dev python-dateutil python-docutils python-feedparser python-gdata python-jinja2 python-ldap python-libxslt1 python-lxml python-mako python-mock python-openid python-psycopg2 python-psutil python-pybabel python-pychart python-pydot python-pyparsing python-reportlab python-simplejson python-tz python-unittest2 python-vatnumber python-vobject python-webdav python-werkzeug python-xlwt python-yaml python-zsi -y 

# Download the tools - All wget should go here
RUN wget https://github.com/samtools/samtools/releases/download/1.2/samtools-1.2.tar.bz2 && \
    wget https://github.com/statgen/bamUtil/archive/master.tar.gz && \
    wget http://sourceforge.net/projects/bio-bwa/files/bwa-0.7.12.tar.bz2 && \
    wget https://s3.amazonaws.com/data-upload-satish/picard.tar.gz && \
    wget http://www.well.ox.ac.uk/bioinformatics/Software/Platypus-latest.tgz && \
    wget https://github.com/samtools/htslib/releases/download/1.3/htslib-1.3.tar.bz2 && \    
    wget https://www.dropbox.com/s/78h8ek7pc55rjyu/SwiftSeq_local_test_v2.tar && \

# make a dnasoft directory to move all the downloaded files
    mkdir /dnasoft && \
    mv /samtools-1.2.tar.bz2 /dnasoft/samtools-1.2.tar.bz2 && \
    mv /master.tar.gz /dnasoft/bamutils.tar.gz && \
    mv /bwa-0.7.12.tar.bz2 /dnasoft/bwa-0.7.12.tar.bz2 && \
    mv /picard.tar.gz /dnasoft/picard.tar.gz && \
    mv /Platypus-latest.tgz /dnasoft/Platypus-latest.tgz && \
    mv /htslib-1.3.tar.bz2 /dnasoft/htslib-1.3.tar.bz2 && \
    mv /SwiftSeq_local_test_v2.tar /dnasoft/SwiftSeq_local_test_v2.tar && \

# untar the gz files inside dnasoft
 cd /dnasoft && \
 tar -xvf /dnasoft/samtools-1.2.tar.bz2 && \
 tar -xvf /dnasoft/bamutils.tar.gz && \
 tar -xvf /dnasoft/bwa-0.7.12.tar.bz2 && \
 tar -xvf /dnasoft/picard.tar.gz && \
 tar -xvf /dnasoft/Platypus-latest.tgz && \
 tar -xvf /dnasoft/htslib-1.3.tar.bz2 && \
 tar -xvf /dnasoft/SwiftSeq_local_test_v2.tar && \

# Installation of all the tools as per standary documentation
     cd /dnasoft/bamUtil-master/ && \
        make cloneLib && \
        make  && \
        make install INSTALLDIR=/dnapipeline && \

     cd /dnasoft/samtools-1.2 && \
        make && \
        make install && \
        make prefix=/dnapipeline && \ 

     cd /dnasoft/bwa-0.7.12 && \
        make && \ 

     cd /dnasoft/broadinstitute-picard-3a81eb1/ && \
        git config --global http.sslVerify false && git clone https://github.com/samtools/htsjdk.git && \
        ant clean all && \
        mv dist/picard.jar picard.jar && \
        mv src/scripts/picard/docker_helper.sh docker_helper.sh && \
        ant clean && \
        rm -rf htsjdk && \
        rm -rf src && \
        rm -rf lib && \
        rm build.xml && \
 
     cd /dnasoft/htslib-1.3 && \
        ./configure && \
        make install && \
        make && \

     cd /dnasoft/Platypus_0.8.1 && \
        ./buildPlatypus.sh  && \

# Installing Swift
     cd /dnasoft && \   
     git clone https://github.com/swift-lang/swift-k.git swift-0.96 && \
     cd swift-0.96/ && \
     git checkout -b release-0.96-swift && \
     ant redist


# Clean Up

RUN rm -rf /dnasoft/Platypus-latest.tgz && \
    rm -rf /dnasoft/SwiftSeq_local_test_v2.tar && \
    rm -rf /dnasoft/bwa-0.7.12.tar.bz2 && \
    rm -rf /dnasoft/htslib-1.3.tar.bz2 && \
    rm -rf /dnasoft/samtools-1.2.tar.bz2 && \
    rm -rf /dnasoft/picard.tar.gz && \
    rm -rf /dnasoft/bamutils.tar.gz 

# Set PATH
ENV LD_LIBRARY_PATH /dnasoft/htslib-1.3/
ENV PATH /dnasoft/Platypus_0.8.1/:$PATH
ENV PATH /dnasoft/bamUtil-master/bin:$PATH
ENV PATH /dnasoft/bwa-0.7.12:$PATH
ENV PATH /dnasoft/samtools-1.2:$PATH
ENV PATH /dnasoft/SwiftSeq_local_test/executable:$PATH
# Finally, set the workdir to /dnasoft so that the docker image runs from this path.
WORKDIR /dnasoft
