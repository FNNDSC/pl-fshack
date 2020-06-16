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
import pudb

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

        python fshack.py                                              \\
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


"""


class Fshack(ChrisApp):
    """
    This app will house a complete FreeSurfer install and run it via the plugin.
    """
    AUTHORS = 'FNNDSC (dev@babyMRI.org)'
    SELFPATH = os.path.dirname(os.path.abspath(__file__))
    SELFEXEC = os.path.basename(__file__)
    EXECSHELL = 'python3'
    TITLE = 'A quick-n-dirty attempt at hacking a FreeSurfer ChRIS plugin'
    CATEGORY = ''
    TYPE = 'ds'
    DESCRIPTION = 'This app will house a complete FreeSurfer install and run it via the plugin'
    DOCUMENTATION = 'http://wiki'
    VERSION = '0.1'
    ICON = ''  # url of an icon image
    LICENSE = 'Opensource (MIT)'
    MAX_NUMBER_OF_WORKERS = 1  # Override with integer value
    MIN_NUMBER_OF_WORKERS = 1  # Override with integer value
    MAX_CPU_LIMIT = ''  # Override with millicore value as string, e.g. '2000m'
    MIN_CPU_LIMIT = ''  # Override with millicore value as string, e.g. '2000m'
    MAX_MEMORY_LIMIT = ''  # Override with string, e.g. '1Gi', '2000Mi'
    MIN_MEMORY_LIMIT = ''  # Override with string, e.g. '1Gi', '2000Mi'
    MIN_GPU_LIMIT = 0  # Override with the minimum number of GPUs, as an integer, for your plugin
    MAX_GPU_LIMIT = 0  # Override with the maximum number of GPUs, as an integer, for your plugin

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
        # self.add_argument("-s", "--subjectID",
        #                     help        = "The subject directory",
        #                     type        = str,
        #                     dest        = 'subjectID',
        #                     optional    = True,
        #                     default     = "")
        self.add_argument("-a", "--args",
                          help="FS arguments to pass",
                          type=str,
                          dest='args',
                          optional=True,
                          default="")
        self.add_argument("-e", "--exec",
                          help="FS app to run",
                          type=str,
                          dest='exec',
                          optional=True,
                          default="recon-all")
        self.add_argument("-i", "--inputFile",
                          help="input file",
                          type=str,
                          dest='inputFile',
                          optional=False,
                          default="")
        self.add_argument("-o", "--outputFile",
                          help="output file",
                          type=str,
                          dest='outputFile',
                          optional=False,
                          default="")

    def get_first_file(self, directory):
        for file in os.listdir(directory):
            if file.endswith(".dcm"):
                return file
            elif file.endswith(".nii"):
                return file

    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """
        global str_cmd
        print(Gstr_title)
        print('Version: %s' % self.get_version())

        # get first file inside of the directory
        str_inputFile = self.get_first_file(options.inputdir)

        l_appargs = options.args.split('ARGS:')
        if len(l_appargs) == 2:
            str_args = l_appargs[1]
        else:
            str_args = l_appargs[0]

        if options.exec == 'recon-all':  # -all -notalairach -parallel -openmp %d
            str_cmd = '/usr/local/freesurfer/bin/%s -i %s/%s -subjid %s/%s %s' % \
                      (options.exec, options.inputdir, options.inputFile,
                       options.outputdir, options.outputFile, str_args)

        if options.exec == 'mri_convert':  # --split -zo
            str_cmd = '/usr/local/freesurfer/bin/%s %s/%s  %s/%s %s' % \
                      (options.exec, options.inputdir, options.inputFile,
                       options.outputdir, options.outputFile, str_args)

        if options.exec == 'mri_info':  # --conformed --type
            str_cmd = '/usr/local/freesurfer/bin/%s %s/%s %s > %s/%s' % \
                      (options.exec, options.inputdir, options.inputFile,
                       str_args, options.outputdir, options.outputFile)

        if options.exec == 'mris_info':  # --ncols #nrows
            str_cmd = '/usr/local/freesurfer/bin/%s %s/%s %s > %s/%s' % \
                      (options.exec, options.inputdir, options.inputFile,
                       str_args, options.outputdir, options.outputFile)
        # pudb.set_trace()
        os.system(str_cmd)

    def show_man_page(self):
        """
        Print the app's man page.
        """
        print(Gstr_synopsis)


# ENTRYPOINT
if __name__ == "__main__":
    chris_app = Fshack()
    chris_app.launch()
