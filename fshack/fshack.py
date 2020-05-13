#!/usr/bin/env python                                            
#
# fshack ds ChRIS plugin app
#
# (c) 2016-2019 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#


import os
import sys
sys.path.append(os.path.dirname(__file__))

# import the Chris app superclass
from chrisapp.base import ChrisApp


Gstr_title = """

  __     _                _    
 / _|   | |              | |   
| |_ ___| |__   __ _  ___| | __
|  _/ __| '_ \ / _` |/ __| |/ /
| | \__ \ | | | (_| | (__|   < 
|_| |___/_| |_|\__,_|\___|_|\_\
                               

"""

Gstr_synopsis = """
    NAME

       fshack.py 

    SYNOPSIS

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

    DESCRIPTION

        This program is meant to be run inside of the container. To run with
        Docker, copy this command and modify as needed:

        docker run -v <pathToInput>:/incoming -v <pathToOutput>:/outgoing -ti fnndsc/pl-fshack fshack.py --subjectID <outputName> /incoming /outgoing

        <pathToInput> is the path to your input files
        <pathToOutput> is the path to where you want your output to go
        <outputName> is the name of the output directory

        The path must be an absolute path (in other words, just a specific path).

        Assuming you're on a Windows operating system, this is what it might look
        like:

        Example:

        docker run -v /home/user/desktop:/incoming -v /home/user/desktop:/outgoing -ti fnndsc/pl-fshack fshack.py --subjectID myOutputFiles /incoming /outgoing

        If you want to specify how many processors the plugin will use, 
        add the -p flag (default is 1), then the number of processors.
        It is recommended to allocate as much processors as you can
        spare to speed up the plugin.


        Example:

        docker run -v /home/user/desktop:/incoming -v /home/user/desktop:/outgoing -ti fnndsc/pl-fshack fshack.py --subjectID myOutputFiles /incoming /outgoing -p 4

    ARGS

	-s|--subjectID <subjectDirInsideInputDir>
	A directory *within* the <inputDir> that contains the images for
	recon-all to process.

        -p <numOfProcessors>
        Specifies the number processors that this plugin will run use. Default 
        number is 1.

        [-h] [--help]
        If specified, show help message and exit.
        
        [--json]
        If specified, show json representation of app and exit.
        
        [--man]
        If specified, print (this) man page and exit.

        [--meta]
        If specified, print plugin meta data and exit.
        
        [--savejson <DIR>] 
        If specified, save json representation file to DIR and exit. 
        
        [-v <level>] [--verbosity <level>]
        Verbosity level for app. Not used currently.
        
        [--version]
        If specified, print version number and exit. 

"""


class Fshack(ChrisApp):
    """
    This app will house a complete FreeSurfer install and run it via the plugin.
    """
    AUTHORS                 = 'FNNDSC (dev@babyMRI.org)'
    SELFPATH                = os.path.dirname(os.path.abspath(__file__))
    SELFEXEC                = os.path.basename(__file__)
    EXECSHELL               = 'python3'
    TITLE                   = 'A quick-n-dirty attempt at hacking a FreeSurfer ChRIS plugin'
    CATEGORY                = ''
    TYPE                    = 'ds'
    DESCRIPTION             = 'This app will house a complete FreeSurfer install and run it via the plugin'
    DOCUMENTATION           = 'http://wiki'
    VERSION                 = '0.1'
    ICON                    = '' # url of an icon image
    LICENSE                 = 'Opensource (MIT)'
    MAX_NUMBER_OF_WORKERS   = 1  # Override with integer value
    MIN_NUMBER_OF_WORKERS   = 1  # Override with integer value
    MAX_CPU_LIMIT           = '' # Override with millicore value as string, e.g. '2000m'
    MIN_CPU_LIMIT           = '' # Override with millicore value as string, e.g. '2000m'
    MAX_MEMORY_LIMIT        = '' # Override with string, e.g. '1Gi', '2000Mi'
    MIN_MEMORY_LIMIT        = '' # Override with string, e.g. '1Gi', '2000Mi'
    MIN_GPU_LIMIT           = 0  # Override with the minimum number of GPUs, as an integer, for your plugin
    MAX_GPU_LIMIT           = 0  # Override with the maximum number of GPUs, as an integer, for your plugin

    # Use this dictionary structure to provide key-value output descriptive information
    # that may be useful for the next downstream plugin. For example:
    #
    # {
    #   "finalOutputFile":  "final/file.out",
    #   "viewer":           "genericTextViewer",
    # }
    #
    # The above dictionary is saved when plugin is called with a ``--saveoutputmeta``
    # flag. Note also that all file paths are relative to the system specified
    # output directory.
    OUTPUT_META_DICT = {}

    def define_parameters(self):
        """
        Define the CLI arguments accepted by this plugin app.
        Use self.add_argument to specify a new app argument.
        """
        self.add_argument("-s", "--subjectID",
                            help        = "The subject directory",
                            type        = str,
                            dest        = 'subjectID',
                            optional    = False,
                            default     = "")
        self.add_argument("-p",
                            help        = "Number of processors to use",
                            type        = int,
                            dest        = 'processors',
                            optional    = True,
                            default     = 1)

    def get_first_file(self, directory):
        for file in os.listdir(directory):
            if (file.endswith(".dcm")):
                return file

    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """
        print(Gstr_title)
        print('Version: %s' % self.get_version())
        
        # get first file inside of the directory
        str_inputFile = self.get_first_file(options.inputdir)
        
        os.system('/usr/local/freesurfer/bin/recon-all -i %s/%s -subjid %s/%s -all -notalairach -parallel -openmp %d' % (options.inputdir, str_inputFile, options.outputdir, options.subjectID, options.processors))


    def show_man_page(self):
        """
        Print the app's man page.
        """
        print(Gstr_synopsis)


# ENTRYPOINT
if __name__ == "__main__":
    chris_app = Fshack()
    chris_app.launch()
