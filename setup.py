# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Invenio module for common role based access control."""

import os
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

requirements = [
    'blinker>=1.3.0',
    'Flask-Breadcrumbs>=0.2',
    'Flask-Login>=0.2.7',
    'Flask-Menu>=0.2',
    'Flask-Registry>=0.2',
    'Flask>=0.10.1',
    'mock>=1.0.1',
    'six>=1.7.2',
    'SQLAlchemy-Utils[encrypted]>=0.30.1',
    'SQLAlchemy>=1.0',
    'wtforms-alchemy>=0.13.1',
    'WTForms>=2.0.1',
    'invenio-accounts>=0.1.2',
    'invenio-base>=0.2.1',
    'invenio-ext>=0.1.0',
    'invenio-upgrader>=0.1.0',
    'invenio-utils>=0.1.0',
]

test_requirements = [
    'Flask-Testing>=0.4.1',
    'coverage>=4.0.0',
    'pytest-cov>=2.1.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.0',
    'unittest2>=1.1.0',
    'invenio-testing>=0.1.1',
]


class PyTest(TestCommand):

    """PyTest Test."""

    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        """Init pytest."""
        TestCommand.initialize_options(self)
        self.pytest_args = []
        try:
            from ConfigParser import ConfigParser
        except ImportError:
            from configparser import ConfigParser
        config = ConfigParser()
        config.read('pytest.ini')
        self.pytest_args = config.get('pytest', 'addopts').split(' ')

    def finalize_options(self):
        """Finalize pytest."""
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        """Run tests."""
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('invenio_access', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='invenio-access',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='invenio TODO',
    license='GPLv2',
    author='CERN',
    author_email='info@invenio-software.org',
    url='https://github.com/inveniosoftware/invenio-access',
    packages=[
        'invenio_access',
    ],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'console_scripts': [
            'webaccessadmin ='
            ' invenio_access.scripts.webaccessadmin:main',
        ],
    },
    install_requires=requirements,
    extras_require={
        'docs': [
            'Sphinx>=1.3',
            'sphinx_rtd_theme>=0.1.7'
        ],
        'tests': test_requirements
    },
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        # 'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
        'Development Status :: 1 - Planning',
    ],
    tests_require=test_requirements,
    cmdclass={'test': PyTest},
)
