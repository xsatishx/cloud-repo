# Stampy Dockerile

FROM debian:jessie

# Maintainer 
MAINTAINER Satish Balakrishnan <satish@healthseq.com>

# apt packages and updates
RUN apt-get update && apt-get upgrade -y && apt-get install make automake cmake gcc wget zlib1g-dev ncurses-dev python-dev g++ -y

# install stampy
RUN mkdir /dnasoft \
    && wget -O /dnasoft/stampy-latest.tgz http://www.well.ox.ac.uk/bioinformatics/Software/Stampy-latest.tgz \
    && tar xvf /dnasoft/stampy-latest.tgz -C /dnasoft \ 
    && sed -i 's/-Wl//' /dnasoft/stampy-1.0.28/makefile \
    && chmod -R 777 /dnasoft/stampy-1.0.28 \
    && cd /dnasoft/stampy-1.0.28 \
    && make \
    && cp /dnasoft/stampy-1.0.28/stampy.py /usr/local/bin/ \
    && chmod a+x /usr/local/bin/stampy.py \
    && chmod -R 777 /dnasoft/ \
    && chmod -R 766 /dnasoft/***

# Set Path
ENV PATH /dnasoft/stampy-1.0.28:$PATH

# open ports private only
EXPOSE 8080

# Use baseimage-docker's bash.
CMD ["/bin/bash"]

#Clean up .
RUN rm -rf /dnasoft/stampy-latest.tgz
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN apt-get autoclean && apt-get autoremove -y && rm -rf /var/lib/{apt,dpkg,cache,log}/
