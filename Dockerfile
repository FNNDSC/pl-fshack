# Docker file for fshack ChRIS plugin app
#
# Build with
#
#   docker build -t <name> .
#
# For example if building a local version, you could do:
#
#   docker build -t local/pl-fshack .
#
# In the case of a proxy (located at 192.168.13.14:3128), do:
#
#    docker build --build-arg http_proxy=http://192.168.13.14:3128 --build-arg UID=$UID -t local/pl-fshack .
#
# To run an interactive shell inside this container, do:
#
#   docker run -ti --entrypoint /bin/bash local/pl-fshack
#
# To pass an env var HOST_IP to container, do:
#
#   docker run -ti -e HOST_IP=$(ip route | grep -v docker | awk '{if(NF==11) print $9}') --entrypoint /bin/bash local/pl-fshack
#



FROM fnndsc/ubuntu-python3:latest
# FROM fnndsc/centos-python3:latest
MAINTAINER fnndsc "dev@babymri.org"

ENV APPROOT="/usr/src/fshack" \
    FREESURFER_HOME="/usr/local/freesurfer"
COPY ["fshack", "${APPROOT}"]
COPY ["requirements.txt", "${APPROOT}"]
COPY ["license.txt", "${APPROOT}"]

WORKDIR $APPROOT

# Now add the explicit commands to pull, unpack and "install" 
# FreeSurfer using "RUN ..."
# For ubuntu... apt install ...
RUN apt update && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

RUN apt install -y wget && \
    wget https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/6.0.0/freesurfer-Linux-centos6_x86_64-stable-pub-v6.0.0.tar.gz && \
    tar -C /usr/local -xzvf freesurfer-Linux-centos6_x86_64-stable-pub-v6.0.0.tar.gz && \
    rm -rf freesurfer-Linux-centos6_x86_64-stable-pub-v6.0.0.tar.gz && \
    apt-get -y install bc binutils libgomp1 perl psmisc sudo tar tcsh unzip uuid-dev vim-common libjpeg62-dev && \
    mv license.txt /usr/local/freesurfer

# ENV setup inside freesurfer.env

CMD ["fshack.py", "--help"]