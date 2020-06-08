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
	    -s|--subjectID                                      			\\
            -a|--reconall                                               \\
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

    -a|--reconall
    Speciies all the arguments that FreeSurfer's recon-all accepts

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
    If specified, print version number . 


Run
----

This ``plugin`` can be run as a containerized docker image.

First we need to fetch sample DICOM images. Follow the steps below to fetch sample DICOM images.


- Clone this repository (SAG-anon) to your local computer.

::

    git clone https://github.com/FNNDSC/SAG-anon.git

- Make sure the ``SAG-anon`` directory is placed in the same directory as your ``pl-fshack`` directory.

Using ``docker run``
~~~~~~~~~~~~~~~~~~~~

To run using ``docker``, be sure to assign an "input" directory to ``/incoming`` and an output directory to ``/outgoing``. *Make sure that the* ``/out`` *directory is world writable!*

- Make sure your current working directory is the one which contains both ``SAG-anon`` and ``pl-fshack``.

- Create an output directory named ``results`` in the current working directory.

- Pull the ``fnndsc/pl-fshack`` image using the following command.

::

    docker pull fnndsc/pl-fshack

Copy and modify the command below as needed.

.. code:: bash

    docker run -v /SAG-anon/:/incoming -v /results/:/outgoing   \\
        fnndsc/pl-fshack fshack.py                                          \\
        --subjectID FShackOutput                                            \\
        /incoming /outgoing

The path must be an absolute path (in other words, just a specific path).


More Examples
-------------

To specify "recon-all" arguments:
    (In-Progress)
