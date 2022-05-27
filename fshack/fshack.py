#!/usr/bin/env python
#
# fshack DS ChRIS plugin app
#
# (c) 2016-2022 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#


import  os
import  sys
import  asyncio
import  glob
import  copy
import  itertools
from argparse import Namespace
from typing import Iterator, TextIO
from pathlib import Path
from colorama import Fore
from chris_plugin import PathMapper
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

MAX_CONCURRENT_JOBS = len(os.sched_getaffinity(0))
sem = asyncio.Semaphore(MAX_CONCURRENT_JOBS)

COLORS = itertools.cycle([
    Fore.RED,
    Fore.GREEN,
    Fore.YELLOW,
    Fore.BLUE,
    Fore.MAGENTA,
    Fore.CYAN
])


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
    VERSION                 = '1.3.0'
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

    async def job_run(self, str_cmd, stdout, stderr, subjects_dir: str) -> int:
        """
        Run a command, redirecting its output to file-like objects which support ``write``.

        :param str_cmd: command to run
        :param stdout: writable file-like object
        :param stderr: writable file-like object
        :param subjects_dir: value for ``SUBJECTS_DIR`` environment variable
        :return: subprocess exit code
        """

        localEnv    = os.environ.copy()
        localEnv["SUBJECTS_DIR"] = subjects_dir
        process = await asyncio.create_subprocess_shell(str_cmd, env=localEnv,
                                                        stdout=asyncio.subprocess.PIPE,
                                                        stderr=asyncio.subprocess.PIPE)
        await asyncio.gather(_handle(process.stdout, stdout), _handle(process.stderr, stderr))
        await process.wait()
        return process.returncode

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

        rc = asyncio.run(self.__run_all(options))
        sys.exit(rc)

    async def __run_all(self, options) -> int:
        """
        Process every subject in the input directory in parallel.

        :return: if any subprocesses end with a non-zero exit code, an arbitrary non-zero exit code
                 is returned. Otherwise, ``0`` is returned.
        """
        subjects = self.map_inputs(options)
        results = await asyncio.gather(*(self.process_subject(subject) for subject in subjects))
        for bad_rc in filter(lambda rc: rc != 0, results):
            return bad_rc
        return 0

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

    def map_inputs(self, options: Namespace) -> Iterator[Namespace]:
        """
        Generates plugin instance options objects where ``inputdir`` and ``outputdir``
        are changed to be subdirectories of the given ``options.inputdir`` and ``options.outputdir``.

        In the special case where there are no subdirectories of ``options.inputdir``,
        ``options`` is returned as-is.

        Additionally, a ``display_prefix`` field is set on the produced ``options`` which
        color-codes the output per-subject.
        """
        input_dir = Path(options.inputdir)
        output_dir = Path(options.outputdir)
        mapper = PathMapper.dir_mapper_deep(input_dir, output_dir)
        if mapper.is_empty():
            print('WARNING: mapper is empty, assuming base')
            options.display_prefix = ''
            yield options
            return
        for sub_input, sub_output in mapper:
            options_copy = copy.copy(options)
            options_copy.inputdir = str(sub_input)
            options_copy.outputdir = str(sub_output)
            options_copy.display_prefix = f"{next(COLORS)}({sub_input.relative_to(input_dir)})"
            yield options_copy

    async def process_subject(self, options: Namespace) -> int:
        """
        Run the selected fshack program, while redirecting stdout and stderr to both
        the current process' stdout and stderr ("console" output) as well as "log"
        files in the output directory.

        The "terminal" output is prefixed by ``options.display_prefix``, which should be
        set by ``map_inputs`` to color-code the line and also with a subject identification.

        The ``options`` parameter is mutated.

        This method uses the global ``sem`` object to restrict the number of parallel subprocesses.

        :return: the program's exit code.
        """
        options.inputFile = self.inputFileSpec_parse(options)

        str_cmd = self.create_cmd(options)
        # Run the job and provide realtime stdout
        # and post-run stderr
        os.mkdir(options.outputdir)
        m_stdout = MultiSink((
            PrefixedSink(sys.stdout, prefix=options.display_prefix, suffix=Fore.RESET),
            open(f'{options.outputdir}/{options.outputFile}-stdout', 'w')
        ))
        m_stderr = MultiSink((
            PrefixedSink(sys.stderr, prefix=options.display_prefix, suffix=Fore.RESET),
            open(f'{options.outputdir}/{options.outputFile}-stderr', 'w')
        ))
        with m_stdout as stdout, m_stderr as stderr:
            async with sem:
                rc = await self.job_run(str_cmd, stdout, stderr, options.outputdir)

        with open(f'{options.outputdir}/{options.outputFile}-returncode', 'w') as rc_file:
            rc_file.write(str(rc))

        return rc

    def show_man_page(self):
        """
        Print the app's man page.
        """
        print(Gstr_synopsis)


async def _handle(source: asyncio.StreamReader, sink: TextIO):
    """Stream bytes one-by-one from an async source to a sync sink until EOF."""
    while len(data := await source.read(1)) == 1:
        sink.write(data.decode(encoding='utf-8'))


# ENTRYPOINT
if __name__ == "__main__":
    chris_app = Fshack()
    chris_app.launch()
