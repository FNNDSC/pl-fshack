
import sys
import os


# Make sure we are running python3.5+
if 10 * sys.version_info[0] + sys.version_info[1] < 38:
    sys.exit("Sorry, only Python 3.8+ is supported.")


from setuptools import setup


def readme():
    print("Current dir = %s" % os.getcwd())
    print(os.listdir())
    with open('README.rst') as f:
        return f.read()

setup(
      name             =   'fshack',
      # for best practices make this version the same as the VERSION class variable
      # defined in your ChrisApp-derived Python class
      version          =   '1.5.0',
      description      =   'A containerized FreeSurfer, with several modes of operation accessible via specific CLI patterning',
      long_description =   readme(),
      author           =   'FNNDSC',
      author_email     =   'dev@babyMRI.org',
      url              =   'https://github.com/FNNDSC/pl-fshack',
      packages         =   ['fshack'],
      install_requires =   ['chrisapp', 'pudb'],
      test_suite       =   'nose.collector',
      tests_require    =   ['nose'],
      scripts          =   ['fshack/fshack.py'],
      license          =   'MIT',
      zip_safe         =   False
     )
