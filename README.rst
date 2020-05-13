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
	    -s|--subjectID <subjectDirInsideInputDir>			\\
            -p <numOfProcessors>                                        \\
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

    -p <numOfProcessors>
    Specifies the number processors that this plugin will run use. Default 
    number is 1.

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



Using ``docker run``
~~~~~~~~~~~~~~~~~~~~

To run using ``docker``, be sure to assign an "input" directory to ``/incoming`` and an output directory to ``/outgoing``. *Make sure that the* ``/out`` *directory is world writable!*

Copy and modify the command below as needed.

.. code:: bash

    docker run -v <pathToInput>:/incoming -v <pathToOutput>:/outgoing -ti fnndsc/pl-fshack fshack.py --subjectID <outputName> /incoming /outgoing

<pathToInput> is the path to your input files
<pathToOutput> is the path to where you want your output to go
<outputName> is the name of the output directory

The path must be an absolute path (in other words, just a specific path).

If you want to specify how many processors this plugin will use, 
add the -p flag (default is 1), then the number of processors.
It is recommended to allocate as much processors as you can
spare to speed up the plugin.

Examples
--------

Assuming you're on a Windows operating system, this is what it might look
like:

.. code::
    
    docker run -v /home/user/desktop/myInput:/incoming -v /home/user/desktop/myOutput:/outgoing -ti fnndsc/pl-fshack fshack.py --subjectID myOutputFiles /incoming /outgoing


To specify the number of processors:

.. code::

    docker run -v /home/user/desktop/myInput:/incoming -v /home/user/desktop/myOutput:/outgoing -ti fnndsc/pl-fshack fshack.py --subjectID myOutputFiles /incoming /outgoing -p 4

