from distutils.core import setup
from setuptools import find_packages
import subprocess

setup(name='wafer-thin-mint',
    version='1.0.13',
    author='Simon Chapman - Team Swift',
    author_email='simon.chapman@saffrondigital.com',
    packages=find_packages())

subprocess.call(['pip', 'install', '-r', 'requirements.txt', '--no-deps'])
