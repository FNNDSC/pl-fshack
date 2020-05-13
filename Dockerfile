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

ENV APPROOT="/usr/src/fshack"
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
    wget https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/7.1.0/freesurfer-linux-centos8_x86_64-7.1.0.tar.gz && \
    tar -C /usr/local -xzvf freesurfer-linux-centos8_x86_64-7.1.0.tar.gz && \
    rm -rf freesurfer-linux-centos8_x86_64-7.1.0.tar.gz && \
    apt-get -y install bc binutils libgomp1 perl psmisc sudo tar tcsh unzip uuid-dev vim-common libjpeg62-dev && \
    mv license.txt /usr/local/freesurfer

ENV PATH="/usr/local/freesurfer/bin:/usr/local/freesurfer/fsfast/bin:/usr/local/freesurfer/tktools:/usr/local/freesurfer/mni/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:" \
    FREESURFER_HOME="/usr/local/freesurfer" \
    SUBJECTS_DIR="/outgoing" \
    MINC_LIB_DIR="/usr/local/freesurfer/mni/lib" \
    MNI_DATAPATH="/usr/local/freesurfer/mni/data" \
    PERL5LIB="/usr/local/freesurfer/mni/share/perl5" \
    MINC_BIN_DIR="/usr/local/freesurfer/mni/bin" \
    MNI_PERL5LIB="/usr/local/freesurfer/mni/share/perl5" \
    FMRI_ANALYSIS_DIR="/usr/local/freesurfer/fsfast" \
    FUNCTIONALS_DIR="/usr/local/freesurfer/sessions" \
    LOCAL_DIR="/usr/local/freesurfer/local" \
    FSFAST_HOME="/usr/local/freesurfer/fsfast" \
    MNI_DIR="/usr/local/freesurfer/mni" \
    FSF_OUTPUT_FORMAT="nii.gz"

CMD ["fshack.py", "--help"]