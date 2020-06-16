pl-fshack
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

This app will house a complete FreeSurfer install and run it via the plugin


Synopsis
--------

.. code::

    python fshack.py                                         \\
            -i|--inputFile <inputFileWithinInputDir>                  \\
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

``fshack.py`` is a ChRIS-based application that uses Docker to containerize
**FreeSurfer**, a brain imaging software, and simplifying the steps needed to
run that software. With some input files and Docker installed, you can run the
brain imaging software in no time!


Arguments
---------

.. code::

    -i|--inputFile <inputFileWithinInputDir>
    Input file to convert present in inputDir. Typically a DICOM file or a nifti volume.

    -o|--outputFile <outputFileWithinOutputDir>
    Output file/directory name to store the output in within the outputDir.
    Note: This argument is used in place of -s|--subjectID <subjID> of FreeSurfer

    [-e|--exec <commandToExec>]
    Specifies the Freesurfer command to execute.

    [-a|--args <argsPassedToExec>]
    Specifies all the arguments within quotes (''), that FreeSurfer's commands:
    recon-all, mri_convert, mri_info, and mris_info accepts.
    Note: Pass the arguments as a string prefixed with 'ARGS: '
    within single quotes 'ARGS:'

    [-h] [--help]
    If specified, show help message.
        
    [--json]
    If specified, show json representation of app.
        
    [--man]
    If specified, print (this) man page.

    [--meta]
    If specified, print plugin meta data.
        
    [--savejson <DIR>] 
    If specified, save json representation file to DIR. 
        
    [--version]
    If specified, print version number.


Run
----

This ``plugin`` can be run as a containerized docker image.

First, create a directory named ``devel`` under your ``/home/user/`` directory.

Then, we need to fetch sample DICOM/NIfTI images.

Pull DICOM
^^^^^^^^^^

- We provide a sample directory of ``.dcm`` images here. (https://github.com/FNNDSC/SAG-anon.git)

- Clone this repository (SAG-anon) to your local computer.

::

    git clone https://github.com/FNNDSC/SAG-anon.git

- Make sure the ``SAG-anon`` directory is placed in the ``devel`` directory.

Pull NIFTI
^^^^^^^^^^

- We provide a sample directory of a ``.nii`` volume here. (https://github.com/FNNDSC/SAG-anon-nii.git)

- Clone this repository (SAG-anon-nii) to your local computer.

::

    git clone https://github.com/FNNDSC/SAG-anon-nii.git

- Make sure the ``SAG-anon-nii`` directory is placed in the ``devel`` directory.

Using ``docker run``
~~~~~~~~~~~~~~~~~~~~

To run using ``docker``, be sure to assign an "input" directory to ``/incoming`` and an output directory to ``/outgoing``. *Make sure that the* ``/out`` *directory is world writable!*

- Make sure your current working directory is ``devel``, the one which contains both ``SAG-anon`` and ``pl-fshack``.

- Create an output directory named ``results`` in ``devel``.

- Pull the ``fnndsc/pl-fshack`` image using the following command.

::

    docker pull fnndsc/pl-fshack

Examples
--------

Copy and modify the different commands below as needed.

- ``recon-all``

.. code:: bash

    docker run -v /home/user/devel/SAG-anon-nii/:/incoming -v /home/user/devel/results/:/outgoing   \\
        fnndsc/pl-fshack fshack.py                                          \\
        -i SAG-anon.nii                                                     \\
        -o FShackOutput                                                     \\
        --exec recon-all                                                    \\
        --args 'ARGS: -all -notalairach'                                    \\
        /incoming /outgoing

- ``mri_convert``

.. code:: bash

    docker run -v /home/user/devel/SAG-anon/:/incoming -v /home/user/devel/results/:/outgoing   \\
        fnndsc/pl-fshack fshack.py                                          \\
        -i 0001-1.3.12.2.1107.5.2.19.45152.2013030808110258929186035.dcm    \\
        -o FShackOutput.nii                                                 \\
        --exec mri_convert                                                  \\
        --args 'ARGS: --split'                                              \\
        /incoming /outgoing

- ``mri_info``

.. code:: bash

    docker run -v /home/user/devel/SAG-anon/:/incoming -v /home/user/devel/results/:/outgoing   \\
        fnndsc/pl-fshack fshack.py                                          \\
        -i 0001-1.3.12.2.1107.5.2.19.45152.2013030808110258929186035.dcm    \\
        -o FShackOutput.txt                                                 \\
        --exec mri_info                                                     \\
        --args 'ARGS: --ncols'                                              \\
        /incoming /outgoing

- ``mris_info``

To run ``mris_info`` we need a typical FreeSurfer curvature file. 

Luckily such typical files exist in the output directory of another ChRIS plugin called ``pl-freesurfer_pp``
Let's run that plugin to generate its output tree and then run ``mris_info`` on one of those outputs. 
Here's how you do it:

.. code:: bash

    docker run --rm -v $(pwd)/:/incoming -v /home/user/devel/pl-fshack/:/outgoing  \\
        fnndsc/pl-freesurfer_pp freesurfer_pp.py       \\
        -c surf                                        \\
        -- /incoming /outgoing

The output of the above command is stored in a directory call ``out`` in the ``pl-fshack`` directory.

A sample curvature file named ``rh.smoothwm`` from the ``out`` directory is passed as the inputFile to the docker command below. 

.. code:: bash

    docker run -v /home/user/devel/pl-fshack/:/incoming -v /home/user/devel/results/:/outgoing   \\
        fnndsc/pl-fshack fshack.py                                          \\
        -i rh.smoothwm                                                      \\
        -o FShackOutput.txt                                                 \\
        --exec mris_info                                                    \\
        --args 'ARGS: --ncols'                                              \\
        /incoming /outgoing

The path must be an absolute path (in other words, just a specific path).

