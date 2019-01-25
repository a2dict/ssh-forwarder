# -*- coding: utf-8 -*-
import sys
from os import path
from distutils.core import setup

if sys.version_info < (3, 7):
    sys.exit('monad requires Python 3.7 or higher')

ROOT_DIR = path.abspath(path.dirname(__file__))
sys.path.insert(0, ROOT_DIR)

setup(
    name='ssh_forwarder',
    version='0.6',
    install_requires=[
        'sshtunnel>=0.1.4',
        'scp>=0.13.0'
    ],
    description='',
    classifiers=[
        'Programming Language :: Python :: 3.7',
    ],
    author='a2dict',
    author_email='a2dict@163.com',
    packages=['ssh_forwarder'],
    license='BSD-New',

)
