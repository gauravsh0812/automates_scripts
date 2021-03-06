FROM  ubuntu:20.04
CMD   bash

# ==============================================================================
# INSTALL SOFTWARE VIA THE UBUNTU PACKAGE MANAGER
# =============================================================================

ARG DEBIAN_FRONTEND=noninteractive

RUN rm /bin/sh && ln -s /bin/bash /bin/sh

RUN apt-get update && \
    apt-get -y --no-install-recommends install apt-utils 

# Use individual commands to prevent excess time usage when re-building
RUN apt-get -y --no-install-recommends install wget git 
RUN apt-get -y --no-install-recommends install gcc build-essential pkg-config
RUN apt-get -y --no-install-recommends install python3-dev python3-pip

# Install Dependencies
RUN pip3 install --upgrade setuptools
RUN pip3 install wheel
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Installing 'Distance' module
RUN wget http://lstm.seas.harvard.edu/latex/third_party/Distance-0.1.3.tar.gz && \
    tar zxf Distance-0.1.3.tar.gz && \
    cd distance && \
    python3 setup.py install

RUN apt-get -y --no-install-recommends install libltdl-dev
RUN wget https://download.imagemagick.org/ImageMagick/download/releases/ImageMagick-7.0.11-0.tar.gz && \
    tar xvzf ImageMagick-7.0.11-0.tar.gz  
RUN cd ImageMagick-7.0.11-0 
RUN ./configure --with-modules 
RUN make && \
    apt-get -y --no-install-recommends make install && \
    ldconfig /usr/local/lib


# Installing pdflatex
RUN apt-get install -y --no-install-recommends texlive-full

# Setting up file system
RUN mkdir /im2markup-docker
WORKDIR /im2markup-docker
VOLUME /im2markup-docker
