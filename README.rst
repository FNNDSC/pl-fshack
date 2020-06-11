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
	    -s|--subjectID                                       	\\
            -e|--exec                                                   \\
            -a|--args                                                   \\
            -i|--inputFile                                              \\
            -o|--outputFile                                             \\
            [-h] [--help]                                               \\
            [--json]                                                    \\
            [--man]                                                     \\
            [--meta]                                                    \\
            [--savejson <DIR>]                                          \\
            [-v <level>] [--verbosity <level>]                          \\
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

    -s|--subjectID <subjectDirInsideInputDir>
	A directory *within* the <inputDir> that contains the images for
	recon-all to process.

    -e|--exec
    Specifies the Freesurfer argument to execute.

    -a|--args
    Specifies all the arguments within quotes (''), that FreeSurfer's
    recon-all, mri_convert, mri_info, and mris_info accepts

    -i|--inputFile
    Input file to convert. Typically a DICOM file or a nifti volume.

    -o|--outputFile
    Output file/directory name to store the output in.

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

First, we need to fetch sample DICOM/NIfTI images.

Pull DICOM
^^^^^^^^^^

- We provide a sample directory of ``.dcm`` images here. (https://github.com/FNNDSC/SAG-anon.git)

- Clone this repository (SAG-anon) to your local computer.

::

    git clone https://github.com/FNNDSC/SAG-anon.git

- Make sure the ``SAG-anon`` directory is placed in the same directory as your ``pl-fshack`` directory.

Pull NIFTI
^^^^^^^^^^

- We provide a sample directory of a ``.nii`` volume here. (https://github.com/FNNDSC/SAG-anon-nii.git)

- Clone this repository (SAG-anon-nii) to your local computer.

::

    git clone https://github.com/FNNDSC/SAG-anon-nii.git

- Make sure the ``SAG-anon-nii`` directory is placed in the same directory as your ``pl-fshack`` directory.

Using ``docker run``
~~~~~~~~~~~~~~~~~~~~

To run using ``docker``, be sure to assign an "input" directory to ``/incoming`` and an output directory to ``/outgoing``. *Make sure that the* ``/out`` *directory is world writable!*

- Make sure your current working directory is the one which contains both ``SAG-anon`` and ``pl-fshack``.

- Create an output directory named ``results`` in the current working directory.

- Pull the ``fnndsc/pl-fshack`` image using the following command.

::

    docker pull fnndsc/pl-fshack

Examples
--------

Copy and modify the command below as needed.

.. code:: bash

    docker run -v /SAG-anon-nii/:/incoming -v /results/:/outgoing   \\
        fnndsc/pl-fshack fshack.py                                          \\
        -i SAG-anon.nii                                                     \\
        -o FShackOutput                                                     \\
        --exec recon-all                                                    \\
        --args '-all -notalairach'                                          \\
        /incoming /outgoing

The path must be an absolute path (in other words, just a specific path).

