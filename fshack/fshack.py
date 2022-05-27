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


import  os
import  sys
import  subprocess
import  glob
import  time
from fshack._output import PrefixedSink, MultiSink

sys.path.append(os.path.dirname(__file__))

# import the Chris app superclass
from    chrisapp.base import ChrisApp
import  pudb

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
            [-i|--inputFile <inputFileWithinInputDir>]                  \\
            [-o|--outputFile <outputFileWithinOutputDir>]               \\
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

        [-i|--inputFile <inputFileWithinInputDir>]
        Input file to process. In most cases this is typically a DICOM file
        or a nifti volume, but is also very dependent on context. This file
        exists within the explictly provided CLI positional <inputDir>. If
        specified as a string that starts with a period '.', then examine the
        <inputDir> and assign the first ls-ordered file in the glob pattern:

                        '*' + <inputFileWithoutPeriod> + '*'

        as the <inputFile>. So, an <inputFile> of '.0001' will assign the first
        file that satisfies the glob

                                    '*0001*'

        as <inputFile>.

        [-o|--outputFile <outputFileWithinOutputDir>]
        Output file/directory name to use within the <outputDir>. Note the
        actual meaning of this usage is contextual to the particular <FSapp>.

        Note: In the case of `recon-all`, this argument maps to the

                -s|--subjectID <subjID>

        CLI flag. This file is specified relative to the explicitly provided
        positional CLI <outputDir>.

        Also note that the <outputFile> string is used to prepend many of the CLI
        -stdout -stderr and -returncode filenames.

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
    VERSION                 = '1.2.0'
    ICON                    = ''  # url of an icon image
    LICENSE                 = 'Opensource (MIT)'
    MAX_NUMBER_OF_WORKERS   = 1  # Override with integer value
    MIN_NUMBER_OF_WORKERS   = 1  # Override with integer value
    MAX_CPU_LIMIT           = ''  # Override with millicore value as string, e.g. '2000m'
    MIN_CPU_LIMIT           = '2000m'  # Override with millicore value as string, e.g. '2000m'
    MAX_MEMORY_LIMIT        = ''  # Override with string, e.g. '1Gi', '2000Mi'
    MIN_MEMORY_LIMIT        = '2000Mi'  # Override with string, e.g. '1Gi', '2000Mi'
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
                          help      = "FS arguments to pass",
                          type      = str,
                          dest      = 'args',
                          optional=True,
                          default   = "")
        self.add_argument("-e", "--exec",
                          help      = "FS app to run",
                          type      = str,
                          dest      = 'exec',
                          optional  = True,
                          default   = "recon-all")
        self.add_argument("-i", "--inputFile",
                          help      = "input file (use .<ext> to find and use the first file with that extension)",
                          type      = str,
                          dest      = 'inputFile',
                          optional  = True,
                          default   = "")
        self.add_argument("-o", "--outputFile",
                          help      = "output file",
                          type      = str,
                          dest      = 'outputFile',
                          optional  = True,
                          default   = "run")

    def job_run(self, str_cmd, stdout, stderr) -> int:
        """
        Run a command, redirecting its output to any number of output streams.
        Output is polled for every 2 seconds and written to the given handles.

        :param str_cmd: command to run
        :param stdout: writable file-like object
        :param stderr: writable file-like object
        :return: subprocess exit code
        """

        localEnv    = os.environ.copy()
        localEnv["SUBJECTS_DIR"] = self.options.outputdir
        p = subprocess.Popen(
                    str_cmd.split(),
                    stdout      = subprocess.PIPE,
                    stderr      = subprocess.PIPE,
                    env         = localEnv
                    )

        # subprocess.Popen can only accept "real" file descriptors as stdout and stderr,
        # not any kind of file-like object, so polling is a necessary workaround.
        # https://stackoverflow.com/questions/19409025/python-stringio-doesnt-work-as-file-with-subrpocess-call
        while p.poll() is not None:
            stdout.write(p.stdout.read())
            stderr.write(p.stderr.read())
            time.sleep(2.0)

        # flush remaining output in case poll finishes very fast
        stdout.write(p.stdout.read())
        stderr.write(p.stderr.read())

        return p.returncode

    def inputFileSpec_parse(self, options):
        """
        Parse the inputFile value and possibly trigger some contentual
        behaviour. Specifically, if the inputFile spec starts with a
        period, '.', then search the inputDir for the first file with
        that substring and assign that file as inputFile.
        """
        str_thisDir:    str     = ''
        str_pattern:    str     = ''
        l_files:        list    = []
        if options.inputFile.startswith('.'):
            str_pattern     = options.inputFile[1:]
            str_thisDir     = os.getcwd()
            os.chdir(options.inputdir)
            l_files         = glob.glob('*' + str_pattern + '*')
            if len(l_files):
                return l_files[0]
            os.chdir(str_thisDir)
        return options.inputFile

    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """
        print(Gstr_title)
        print('Version: %s' % self.get_version())
        for k,v in options.__dict__.items():
            print("%20s:  -->%s<--" % (k, v))
        self.options    = options

        options.inputFile = self.inputFileSpec_parse(options)

        str_cmd = self.create_cmd(options)
        # Run the job and provide realtime stdout
        # and post-run stderr
        m_stdout = MultiSink((
            PrefixedSink(sys.stdout, f"({options.inputFile})"),
            open(f'{options.outputdir}/{options.outputFile}-stdout', 'w')
        ))
        m_stderr = MultiSink((
            PrefixedSink(sys.stderr, f"({options.inputFile})"),
            open(f'{options.outputdir}/{options.outputFile}-stderr', 'w')
        ))
        with m_stdout as stdout, m_stderr as stderr:
            rc = self.job_run(str_cmd, stdout, stderr)

        with open(f'{options.outputdir}/{options.outputFile}-returncode', 'w') as rc_file:
            rc_file.write(str(rc))

        sys.exit(rc)

    def create_cmd(self, options) -> str:
        """
        Complicated behavior that I moved into a helper method for the sake of hiding it.
        """
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

        return str_cmd

    def show_man_page(self):
        """
        Print the app's man page.
        """
        print(Gstr_synopsis)


# ENTRYPOINT
if __name__ == "__main__":
    chris_app = Fshack()
    chris_app.launch()
