# FreeBayes TOOL
FROM healthseq/base

# Maintainer 
MAINTAINER Satish Balakrishnan <satish@healthseq.com>

# install freebayes
RUN cd /dnasoft \
  && git clone --recursive git://github.com/ekg/freebayes.git \
  && cd /dnasoft/freebayes \
  && make \
  && chmod -R 777 /dnasoft/freebayes \
  && cp -v /dnasoft/freebayes/bin/* /usr/local/bin

# Permissions
RUN chmod -R 777 /dnasoft

# Set Path
ENV PATH /dnasoft/freebayes/bin:$PATH

# Set the workdir to /dnasoft so that the docker image runs from this path.
WORKDIR /dnasoft/FastQC

#Clean up APT when done.
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN apt-get autoclean && apt-get autoremove -y && rm -rf /var/lib/{apt,dpkg,cache,log}/





