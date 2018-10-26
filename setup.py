# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for common role based access control."""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'SQLAlchemy-Continuum>=1.2.1',
    'Werkzeug>=0.11.2',
    'check-manifest>=0.25',
    'coverage>=4.0',
    'isort>=4.3.0',
    'mock>=1.0.0',
    'pydocstyle>=1.0.0',
    'pytest-cov>=1.8.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.0',
    'redis>=2.10.3',
]

extras_require = {
    'docs': [
        'Sphinx>=1.4.2',
    ],
    'mysql': [
        'invenio-db[mysql]>=1.0.0',
    ],
    'postgresql': [
        'invenio-db[postgresql]>=1.0.0',
    ],
    'sqlite': [
        'invenio-db>=1.0.0',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    if name in ('sqlite', 'mysql', 'postgresql'):
        continue
    extras_require['all'].extend(reqs)

setup_requires = [
    'Babel>=1.3',
    'pytest-runner>=2.6.2',
]

install_requires = [
    'Flask>=0.11.1',
    'Flask-BabelEx>=0.9.3',
    'invenio-accounts>=1.0.2',
    'six>=1.10',
]

packages = find_packages()

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
    keywords='invenio access',
    license='MIT',
    author='CERN',
    author_email='info@inveniosoftware.org',
    url='https://github.com/inveniosoftware/invenio-access',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'flask.commands': [
            'access = invenio_access.cli:access',
        ],
        'invenio_access.actions': [
            'invenio_access.actions = '
            'invenio_access.permissions:superuser_access',
        ],
        'invenio_access.system_roles': [
            'any_user = invenio_access.permissions:any_user',
            'authenticated_user = '
            'invenio_access.permissions:authenticated_user',
        ],
        'invenio_admin.views': [
            'invenio_access_action_users = '
            'invenio_access.admin:action_users_adminview',
            'invenio_access_action_roles = '
            'invenio_access.admin:action_roles_adminview',
            'invenio_access_action_system_roles = '
            'invenio_access.admin:action_system_roles_adminview',
        ],
        'invenio_base.api_apps': [
            'invenio_access = invenio_access:InvenioAccess',
        ],
        'invenio_base.apps': [
            'invenio_access = invenio_access:InvenioAccess',
        ],
        'invenio_db.alembic': [
            'invenio_access = invenio_access:alembic',
        ],
        'invenio_db.models': [
            'invenio_access = invenio_access.models',
        ],
        'invenio_i18n.translations': [
            'messages = invenio_access',
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Development Status :: 5 - Production/Stable',
    ],
)
