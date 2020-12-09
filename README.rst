..
    This file is part of Invenio.
    Copyright (C) 2015-2018 CERN.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

================
 Invenio-Access
================

.. image:: https://img.shields.io/github/license/inveniosoftware/invenio-access.svg
        :target: https://github.com/inveniosoftware/invenio-access/blob/master/LICENSE

.. image:: https://github.com/inveniosoftware/invenio-access/workflows/CI/badge.svg
        :target: https://github.com/inveniosoftware/invenio-access/actions?query=workflow%3ACI

.. image:: https://img.shields.io/coveralls/inveniosoftware/invenio-access.svg
        :target: https://coveralls.io/r/inveniosoftware/invenio-access

.. image:: https://img.shields.io/pypi/v/invenio-access.svg
        :target: https://pypi.org/pypi/invenio-access


Role-based access control (RBAC) for Invenio.

Invenio-Access works together with Invenio-Accounts to provide a full-fledge
authentication and authorization system for Flask and Invenio based on a suite
of existing Flask extensions such as:

- Flask-Security
- Flask-Login
- Flask-Principal
- passlib

Features:

* Role-based access control with object level permissions.
* CLI and administration interface for allowing/denying actions to users, roles
  or system roles.
* Support for superuser privileges.

Further documentation is available on
https://invenio-access.readthedocs.io/
