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


setup_options = dict(
    name='portlycli',
    version=find_version("portlycli", "__init__.py"),
    description='Handy stuff for Portal.',
    long_description=read('README.rst'),
    author='Ben Hall',
    scripts=['bin/portly', 'bin/portly.cmd'],
    packages=find_packages(exclude=['tests*']),
    license="GNU General Public License, version 3",
)

setup(**setup_options)
