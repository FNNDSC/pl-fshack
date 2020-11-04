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
# In the case of a proxy (located at say 10.41.13.4:3128), do:
#
#    export PROXY="http://10.41.13.4:3128"
#    docker build --build-arg http_proxy=${PROXY} --build-arg UID=$UID -t local/pl-fshack .
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
LABEL maintainer="dev@babymri.org"

ARG UID=1001
ENV APPROOT="/usr/src/fshack"
ENV UID=$UID DEBIAN_FRONTEND=noninteractive
COPY ["fshack/", "requirements.txt", "license.txt", "${APPROOT}/"]

WORKDIR $APPROOT

RUN pip install -r requirements.txt                         \
    && apt-get update -q &&                                 \
    apt-get -qq install bc binutils libgomp1 perl psmisc curl tar tcsh uuid-dev vim-common libjpeg62-dev \
    libglu1-mesa libxmu6 libglib2.0-0 qt5-default &&        \
    curl https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/7.1.0/freesurfer-linux-centos8_x86_64-7.1.0.tar.gz | \
    tar -C /usr/local -xz                                   \
    && mv license.txt /usr/local/freesurfer                 \
    && apt-get install -y locales                           \
    && export LANGUAGE=en_US.UTF-8                          \
    && export LANG=en_US.UTF-8                              \
    && export LC_ALL=en_US.UTF-8                            \
    && locale-gen en_US.UTF-8                               \
    && dpkg-reconfigure locales                             \
    && useradd -u $UID -ms /bin/bash localuser

ENV PATH="/usr/local/freesurfer/bin:/usr/local/freesurfer/fsfast/bin:/usr/local/freesurfer/tktools:/usr/local/freesurfer/mni/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:" \
    FREESURFER_HOME="/usr/local/freesurfer"                 \
    SUBJECTS_DIR="/outgoing"                                \
    MINC_LIB_DIR="/usr/local/freesurfer/mni/lib"            \
    MNI_DATAPATH="/usr/local/freesurfer/mni/data"           \
    PERL5LIB="/usr/local/freesurfer/mni/share/perl5"        \
    MINC_BIN_DIR="/usr/local/freesurfer/mni/bin"            \
    MNI_PERL5LIB="/usr/local/freesurfer/mni/share/perl5"    \
    FMRI_ANALYSIS_DIR="/usr/local/freesurfer/fsfast"        \
    FUNCTIONALS_DIR="/usr/local/freesurfer/sessions"        \
    LOCAL_DIR="/usr/local/freesurfer/local"                 \
    FSFAST_HOME="/usr/local/freesurfer/fsfast"              \
    MNI_DIR="/usr/local/freesurfer/mni"                     \
    FSF_OUTPUT_FORMAT="nii.gz"

CMD ["fshack.py", "--help"]
