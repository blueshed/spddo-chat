#!/usr/bin/env python

from setuptools import setup, find_packages

version = '0.002'

setup(name='spddo-chat',
      version=version,
      packages=find_packages('src',exclude=['spddo.chat.tests*']),
      include_package_data = True, 
      exclude_package_data = { '': ['*tests/*'] },
      install_requires = [
        'setuptools',
        'tornado>=4.2',
        'iron-mq>=0.7',
      ],
      entry_points = {
      'console_scripts' : [
                           'chat = spddo.chat.server:main'
                           ]
      },)