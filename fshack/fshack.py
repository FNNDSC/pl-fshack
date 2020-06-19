#!/usr/bin/env python
#
# fshack DS ChRIS plugin app
#
# (c) 2016-2020 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#


import os
import sys
import subprocess

sys.path.append(os.path.dirname(__file__))

# import the Chris app superclass
from chrisapp.base import ChrisApp
import pudb

Gstr_title = """

  __     _                _
 / _|   | |              | |
| |_ ___| |__   __ _  ___| | __  _ __  _   _
|  _/ __| '_ \ / _` |/ __| |/ / | '_ \| | | |
| | \__ \ | | | (_| | (__|   < _| |_) | |_| |
|_| |___/_| |_|\__,_|\___|_|\_(_) .__/ \__, |
                                | |     __/ |
                                |_|    |___/


"""

Gstr_synopsis = """
    NAME

       fshack.py

    SYNOPSIS

        python fshack.py                                                \\
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

        This ChRIS DS plugin contains a complete FreeSurfer

                https://surfer.nmr.mgh.harvard.edu/fswiki/rel7downloadsversion

        distribution. Not all FreeSurfer internal applications are exposed at
        the plugin level, however. At time of writing, the following FreeSurfer
        applications are directly accessible from the plugin CLI:

            * recon-all
            * mri_convert
            * mri_info
            * mris_info

        This plugin is meant to demonstrate some design patterns as well
        as providing some utility for running FreeSurfer within the context
        of ChRIS. It is not meant nor intended to be a canonical FreeSurfer
        ChRIS plugin -- as explicitly indicated by the name, FreeSurfer "hack",
        `fshack`. Colloquially, however, this plugin is also known as `f-shack`.

    ARGS

        -i|--inputFile <inputFileWithinInputDir>
        Input file to process. In most cases this is typically a DICOM file
        or a nifti volume, but is also very dependent on context. This file
        exists within the explictly provided CLI positional <inputDir>.

        -o|--outputFile <outputFileWithinOutputDir>
        Output file/directory name to store the output in within the outputDir.
        Note: In the case of `recon-all`, this argument maps to the

                -s|--subjectID <subjID>

        CLI flag. This file is specified relative to the explicitly provided
        positional CLI <outputDir>.

        [-e|--exec <commandToExec>]
        Specifies the FreeSurfer command within the plugin/container to
        execute.

        Note that only a few of the FreeSurfer apps are currently exposed!

        [-a|--args <argsPassedToExec>]
        Optional string of additional arguments to "pass through" to the
        FreeSurfer app.

        The design pattern of this plugin is to provide all the CLI args for
        a single app specificed `-exec` somewhat blindly. To this end, all the
        args for a given internal FreeSurfer app are themselves specified at
        the plugin level with this flag. These args MUST be contained within
        single quotes (to protect them from the shell) and the quoted string
        MUST start with the required keyword 'ARGS: '.

        If the `--exec <FSapp>` does not require additional CLI args, then
        this `--args <args>` can be safely omitted.

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
    DESCRIPTION  = '''
        This app houses a complete FreeSurfer distro and exposes some
        FreeSurfer apps at the level of the plugin CLI.'
    '''
    AUTHORS                 = 'FNNDSC (dev@babyMRI.org)'
    SELFPATH                = os.path.dirname(os.path.abspath(__file__))
    SELFEXEC                = os.path.basename(__file__)
    EXECSHELL               = 'python3'
    TITLE                   = 'A quick-n-dirty attempt at hacking a FreeSurfer ChRIS plugin'
    CATEGORY                = ''
    TYPE                    = 'ds'
    DOCUMENTATION           = 'https://github.com/FNNDSC/pl-fshack'
    VERSION                 = '1.1.2'
    ICON                    = ''  # url of an icon image
    LICENSE                 = 'Opensource (MIT)'
    MAX_NUMBER_OF_WORKERS   = 1  # Override with integer value
    MIN_NUMBER_OF_WORKERS   = 1  # Override with integer value
    MAX_CPU_LIMIT           = ''  # Override with millicore value as string, e.g. '2000m'
    MIN_CPU_LIMIT           = ''  # Override with millicore value as string, e.g. '2000m'
    MAX_MEMORY_LIMIT        = ''  # Override with string, e.g. '1Gi', '2000Mi'
    MIN_MEMORY_LIMIT        = ''  # Override with string, e.g. '1Gi', '2000Mi'
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
        """
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
                          optional=True,
                          default="")

    def job_run(self, str_cmd):
        """
        Running some CLI process via python is cumbersome. The typical/easy 
        path of

                            os.system(str_cmd)

        is deprecated and prone to hidden complexity. The preferred
        method is via subprocess, which has a cumbersome processing
        syntax. Still, this method runs the `str_cmd` and returns the
        stderr and stdout strings as well as a returncode.

        Providing readtime output of both stdout and stderr seems
        problematic. The approach here is to provide realtime
        output on stdout and only provide stderr on prcoess completion.

        """
        d_ret = {
            'stdout':       "",
            'stderr':       "",
            'returncode':   0
        }

        p = subprocess.Popen(
                    str_cmd.split(),
                    stdout      = subprocess.PIPE,
                    stderr      = subprocess.PIPE,
        )

        # Realtime output on stdout
        str_stdoutLine  = ""
        str_stdout      = ""
        while True:
            stdout      = p.stdout.readline()
            if p.poll() is not None:
                break
            if stdout:
                str_stdoutLine = stdout.decode()
                print(str_stdoutLine, end = '')
                str_stdout      += str_stdoutLine
        d_ret['stdout']     = str_stdout
        d_ret['stderr']     = p.stderr.read().decode()
        d_ret['returncode'] = p.returncode
        print('\nstderr: \n%s' % d_ret['stderr'])
        return d_ret

    def job_stdwrite(self, d_job, options):
        """
        Capture the d_job entries to respective files.
        """
        for key in d_job.keys():
            with open(
                '%s/%s-%s' % (options.outputdir, options.outputFile, key), "w"
            ) as f:
                f.write(str(d_job[key]))
                f.close()
        return {
            'status': True
        }

    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """
        global str_cmd
        print(Gstr_title)
        print('Version: %s' % self.get_version())

        str_args    = ""
        l_appargs   = options.args.split('ARGS:')
        if len(l_appargs) == 2:
            str_args = l_appargs[1]
        else:
            str_args = l_appargs[0]

        str_FSbinDir    = '/usr/local/freesurfer/bin'
        str_cmd         = ""
        if options.exec == 'recon-all':
            str_cmd = '%s/%s -i %s/%s -subjid %s/%s %s ' % \
                      (str_FSbinDir,
                       options.exec, options.inputdir, options.inputFile,
                       options.outputdir, options.outputFile, str_args)

        if options.exec == 'mri_convert':
            str_cmd = '%s/%s %s/%s  %s/%s %s ' % \
                      (str_FSbinDir,
                       options.exec, options.inputdir, options.inputFile,
                       options.outputdir, options.outputFile, str_args)

        if options.exec == 'mri_info':
            str_cmd = '%s/%s %s/%s %s ' % \
                      (str_FSbinDir,
                       options.exec, options.inputdir, options.inputFile,
                       str_args)

        if options.exec == 'mris_info':
            str_cmd = '%s/%s %s/%s %s' % \
                      (str_FSbinDir,
                       options.exec, options.inputdir, options.inputFile,
                       str_args)

        # Run the job and provide realtime stdout
        # and post-run stderr
        self.job_stdwrite(
            self.job_run(str_cmd), options
        )

    def show_man_page(self):
        """
        Print the app's man page.
        """
        print(Gstr_synopsis)


# ENTRYPOINT
if __name__ == "__main__":
    chris_app = Fshack()
    chris_app.launch()
