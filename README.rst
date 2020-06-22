``pl-fshack``
================================

.. image:: https://badge.fury.io/py/fshack.svg
    :target: https://badge.fury.io/py/fshack

.. image:: https://travis-ci.org/FNNDSC/fshack.svg?branch=master
    :target: https://travis-ci.org/FNNDSC/fshack

.. image:: https://img.shields.io/badge/python-3.5%2B-blue.svg
    :target: https://badge.fury.io/py/pl-fshack

.. contents:: Table of Contents


Abstract
--------

This ChRIS ``DS`` plugin contains a complete FreeSurfer (https://surfer.nmr.mgh.harvard.edu/fswiki/rel7downloadsversion) distribution. Not all FreeSurfer internal applications are exposed at the plugin level, however. At time of writing, the following FreeSurfer applications are exposed:

* ``recon-all``
* ``mri_convert``
* ``mri_info``
* ``mris_info``

This plugin is meant to demonstrate some design patterns as well as providing some utility for running FreeSurfer within the context of ChRIS. It is not meant nor intended to be a canonical FreeSurfer ChRIS plugin -- as explicitly indicated by the name, FreeSurfer "hack", ``fshack``. Colloquially, however, this plugin is also known as ``f-shack``.

Thus, while some additional internal FreeSurfer apps might be exposed at the level of the plugin entry point, the intention with this plugin is *not* to necessarily expose *all* FreeSurfer applications. Arguably, more specific and more lightweight containers and/or ChRIS plugins might be more suitable for such pervasive fine-grained coverage.

Alternatively, ``pl-fshack`` does provide a full containerized FreeSurfer distribution, so the plugin could be run with an ``--entrypoint /bin/bash`` to gain access to all the underlying FreeSurfer apps (this however would not the use case in the ChRIS system -- in ChRIS only apps exposed by the plugin interface can be used).

From a design perspective, the main plugin programming problem revolved around exposing some random internal FreeSurfer application with the plugin requirement of needing explicit positional arguments for ``<inputdir>`` and ``<outputdir>``. Since such directory components are for the most part not explicitly used at the CLI level by FreeSurfer apps, the exposure/mapping problem becomes one of correctly constructing the CLI pattern for a given FreeSurfer application to be explicitly aware of these requirements.

Also, the concept of a ChRIS plugin is built on the assumption of no user interactivity. Thus, GUI applications of FreeSurfer are not exposed nor intended to be (but could in theory still be run from the container in a more "manual" fashion). Other FreeSurfer applications that typically provide information at a TTY level, such as ``mri_info`` that just dumps output to "screen" have that same output here explicitly saved to an output text file, specified while calling the plugin appropriately.

The design pattern of this plugin is to allow a user to run some internal FreeSurfer app via the ``--exec`` CLI and to pass whatever command line arguments are applicable to that app via a ``--args`` CLI. Note that to properly parse this ``--args``, the argument to this flag **MUST** be contained within single quotes and **MUST** start with a string ``ARGS:``. Hence

.. code::

    --exec "recon-all" --args 'ARGS: -all -notalairach'

Note that if an underlying FreeSurfer application does not need additional arguments beyond the input and/or output specifications, the ``--args ...`` can be safely omitted.

Synopsis
--------

.. code::

    python fshack.py                                                    \\
            -i|--inputFile <inputFileWithinInputDir>                    \\
            -o|--outputFile <outputFileWithinOutputDir>                 \\
            [-e|--exec <commandToExec>]                                 \\
            [-a|--args <argsPassedToExec> ]                             \\
            [-h] [--help]                                               \\
            [--json]                                                    \\
            [--man]                                                     \\
            [--meta]                                                    \\
            [--savejson <DIR>]                                          \\
            [-v|--verbosity <level>]                                    \\
            [--version]                                                 \\
            <inputDir>                                                  \\
            <outputDir> 

Description
-----------

``fshack.py`` is a ChRIS-based ``DS`` plugin that provides **FreeSurfer** (https://freesurfer.nmr.mgh.harvard.edu) within the ChRIS platform. While the plugin adheres to ChRIS execute requirements, the actual container can in theory also be used as YAFSDC (Yet-Another-FreeSurfer-Docker-Container).

Arguments
---------

.. code::

    -i|--inputFile <inputFileWithinInputDir>
    Input file to process. In most cases this is typically a DICOM file or a nifti volume,
    but is also very dependent on context. This file exists within the explictly provided CLI
    positional <inputDir>.

    -o|--outputFile <outputFileWithinOutputDir>
    Output file/directory name to store the output in within the outputDir.
    Note: In the case of `recon-all`, this argument maps to the  
    
            -s|--subjectID <subjID> 
            
    CLI flag. This file is specified relative to the explicitly provided positional
    CLI <outputDir>.

    [-e|--exec <commandToExec>]
    Specifies the FreeSurfer command within the plugin/container to execute. 
    
    Note that only a few of the FreeSurfer apps are currently exposed!

    [-a|--args <argsPassedToExec>]
    Optional string of additional arguments to "pass through" to the FreeSurfer app.
    
    The design pattern of this plugin is to provide all the CLI args for a single app
    specificed `-exec` somewhat blindly. To this end, all the args for a given internal
    FreeSurfer app are themselves specified at the plugin level with this flag. These
    args MUST be contained within single quotes (to protect them from the shell) and 
    the quoted string MUST start with the required keyword 'ARGS: '.

    [-h] [--help]
    If specified, show some help.
        
    [--json]
    If specified, show the JSON representation of this plugin.
        
    [--man]
    If specified, print (this) man page.

    [--meta]
    If specified, print plugin meta data.
        
    [--savejson <DIR>] 
    If specified, save JSON representation file to DIR. 
        
    [--version]
    If specified, print version number and exit.


Run
----

While ``pl-fshack`` is meant to be run as a containerized docker image, typcially within ChRIS, it is quite possible to run the plugin directly from the command line as well. The following instructions are meant to be a psuedo- ``jupyter-notebook`` inspired style where if you follow along and copy/paste into a terminal you should be able to run all the examples.

First, let's create a directory, say ``devel`` where-ever you feel like it. We will place some test data in this directory to process with this plugin.

.. code::

    cd ~/
    mkdir devel
    cd devel
    export DEVEL=$(pwd)

Now, we need to fetch sample data.

Pull DICOM
^^^^^^^^^^

- We provide a sample directory of anonymous ``.dcm`` images here: (https://github.com/FNNDSC/SAG-anon.git)

- Clone this repository (``SAG-anon``) to your local computer.

::

    git clone https://github.com/FNNDSC/SAG-anon.git

- Make sure the ``SAG-anon`` directory is placed in the ``devel`` directory (you should be there already if you are following along)

Pull NIFTI
^^^^^^^^^^

- We provide a sample directory of a ``.nii`` volume here. (https://github.com/FNNDSC/SAG-anon-nii.git)

- Clone this repository (``SAG-anon-nii``) to your local computer.

::

    git clone https://github.com/FNNDSC/SAG-anon-nii.git

- Make sure the ``SAG-anon-nii`` directory is placed in the ``devel`` directory.

Using ``docker run``
~~~~~~~~~~~~~~~~~~~~

To run using ``docker``, be sure to assign an "input" directory to ``/incoming`` and an output directory to ``/outgoing``. *Make sure that the* ``/out`` *directory is world writable!*

- Make sure your current working directory is ``devel``. At this juncture it should contain ``SAG-anon`` and ``SAG-anon-nii``.

- Create an output directory named ``results`` in ``devel``.

.. code::

   mkdir results && chmod 777 results

- Pull the ``fnndsc/pl-fshack`` image using the following command.

.. code::

    docker pull fnndsc/pl-fshack

Examples
--------

Copy and modify the different commands below as needed.

``recon-all``
^^^^^^^^^^^^^

For ``NifTI`` inputs:

.. code:: bash

    docker run --rm                                                         \
        -v ${DEVEL}/SAG-anon-nii/:/incoming -v ${DEVEL}/results/:/outgoing  \
        fnndsc/pl-fshack fshack.py                                          \
        -i SAG-anon.nii                                                     \
        -o recon-of-SAG-anon-nii                                            \
        --exec recon-all                                                    \
        --args 'ARGS: -all -notalairach'                                    \
        /incoming /outgoing
        
For ``DICOM`` inputs:

.. code:: bash

    docker run --rm                                                         \
        -v ${DEVEL}/SAG-anon-nii/:/incoming -v ${DEVEL}/results/:/outgoing  \
        fnndsc/pl-fshack fshack.py                                          \
        -i 0001-1.3.12.2.1107.5.2.19.45152.2013030808110258929186035.dcm    \
        -o recon-of-SAG-anon-dcm                                            \
        --exec recon-all                                                    \
        --args 'ARGS: -all -notalairach'                                    \
        /incoming /outgoing

NOTE: The ``recon-all`` commands will take multiple hours to run to completion!

``mri_convert``
^^^^^^^^^^^^^^

.. code:: bash

    docker run --rm                                                         \
        -v ${DEVEL}/SAG-anon/:/incoming -v ${DEVEL}/results/:/outgoing      \
        fnndsc/pl-fshack fshack.py                                          \
        -i 0001-1.3.12.2.1107.5.2.19.45152.2013030808110258929186035.dcm    \
        -o DCM2NII.nii                                                      \
        --exec mri_convert                                                  \
        /incoming /outgoing

``mri_info``
^^^^^^^^^^^^

The results of the below information query are stored in text files

.. code:: bash 
  
    /outgoing/info-stdout
    /outgoing/info-stderr
    /outgoing/info-returncode
    

.. code:: bash

    docker run --rm                                                         \
        -v ${DEVEL}/SAG-anon/:/incoming -v ${DEVEL}/results/:/outgoing      \
        fnndsc/pl-fshack fshack.py                                          \
        -i 0001-1.3.12.2.1107.5.2.19.45152.2013030808110258929186035.dcm    \
        -o info                                                             \
        --exec mri_info                                                     \
        /incoming /outgoing

``mris_info``
^^^^^^^^^^^^

To run ``mris_info`` we need a typical FreeSurfer curvature file. 

Luckily such typical files exist in the output directory of another ChRIS plugin called ``pl-freesurfer_pp``. Despite the name, the ``pl-freesurfer_pp`` is *NOT* a FreeSurfer container, but merely a simluated one that contains a pre-processed (hence the ``_pp``) set of data generated from a FreeSurfer run.

Let's run that plugin to generate its output tree and then run ``mris_info`` on one of those outputs. Here's how you do it:

.. code:: bash
    docker pull fnndsc/pl-freesurfer_pp
    docker run --rm                                                     \
        -v $(pwd)/:/incoming -v ${DEVEL}/results:/outgoing              \
        fnndsc/pl-freesurfer_pp freesurfer_pp.py                        \
        -c surf                                                         \
        -- /incoming /outgoing

The output of the above command is a directory called ``surf`` that should be located in the ``results`` directory. A sample curvature file named ``rh.smoothwm`` from the ``results/surf`` directory is passed as the inputFile to the docker command below. 

.. code:: bash

    docker run --rm                                                         \
        -v ${DEVEL}/results/surf:/incoming -v ${DEVEL}/results/:/outgoing   \
        fnndsc/pl-fshack fshack.py                                          \
        -i rh.smoothwm                                                      \
        -o mris_info.txt                                                    \
        --exec mris_info                                                    \
        /incoming /outgoing
        
Debug
-----

Finally, let's conclude with some quick notes on debugging this plugin. The debugging process is predicated on the idea of mapping a source code directory into an already existing container, thus "shadowing" or "masking" the existing code and overlaying current work directly within the container.

In this manner, one can debug the plugin without needing to continually rebuild the docker image (which in the case of this FreeSurfer image can take upwards of 15 minutes).

So, assuming the same env variables as above, and assuming that you are in the source repo base directory of the plugin code:

.. code:: bash

    docker run --rm -ti                                                         \
               -v $(pwd)/fshack:/usr/src/fshack                                 \
               -v ${DEVEL}/SAG-anon/:/incoming                                  \
               -v ${DEVEL}/results/:/outgoing                                   \
               fnndsc/pl-fshack fshack.py                                       \
               -i 0001-1.3.12.2.1107.5.2.19.45152.2013030808110258929186035.dcm \       
               -o info                                                          \
               --exec mri_info                                                  \
               /incoming /outgoing

Obviously, adapt the above as needed.

*-30-*
