#!/usr/bin/env python
"""The setup and build script for myTelegramBot."""

import os

from setuptools import setup, find_packages


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


def requirements():
    """Build the requirements list for this project"""
    requirements_list = []

    with open('requirements.txt') as requirements:
        for install in requirements:
            requirements_list.append(install.strip())

    return requirements_list


setup(name='myTelegramBot',
      version='0.0.1',
      author='Alessio Rocchi',
      author_email='rocchi.b.a@gmail.com',
      license='MIT',
      url='https://github.com/blackms/myTelegramBot',
      keywords='Telegram bot, security bot.',
      description='Just another telegram bot.',
      long_description=(read('README.md')),
      packages=find_packages(exclude=['tests*']),
      install_requires=requirements(),
      include_package_data=True,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Operating System :: POSIX :: Linux',
          'Topic :: Communications :: Chat',
          'Topic :: Internet',
          'Topic :: System :: Networking :: Monitoring',
          'Topic :: System :: Systems Administration'
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
      ])
