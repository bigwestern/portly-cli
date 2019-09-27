#!/usr/bin/env python
import os.path
import codecs
import re
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


requires = ['jsonpath-ng>=1.4.3','networkx>=2.2','jsonpickle>=1.2']

setup_options = dict(
    name='portlycli',
    version=find_version("portlycli", "__init__.py"),
    description='CLI utility to move Portal for ArcGIS items between instances.',
    long_description=read('README.rst'),
    author='Ben Hall',
    scripts=['bin/portly', 'bin/portly.cmd'],
    packages=find_packages(exclude=['tests*']),
    install_requires=requires,    
    license="GNU General Public License, version 3",
)

setup(**setup_options)
