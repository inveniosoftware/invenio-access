..
    This file is part of Invenio.
    Copyright (C) 2015 CERN.

    Invenio is free software; you can redistribute it
    and/or modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation; either version 2 of the
    License, or (at your option) any later version.

    Invenio is distributed in the hope that it will be
    useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Invenio; if not, write to the
    Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
    MA 02111-1307, USA.

    In applying this license, CERN does not
    waive the privileges and immunities granted to it by virtue of its status
    as an Intergovernmental Organization or submit itself to any jurisdiction.

================
 Invenio-Access
================

.. image:: https://img.shields.io/travis/inveniosoftware/invenio-access.svg
        :target: https://travis-ci.org/inveniosoftware/invenio-access

.. image:: https://img.shields.io/coveralls/inveniosoftware/invenio-access.svg
        :target: https://coveralls.io/r/inveniosoftware/invenio-access

.. image:: https://img.shields.io/github/tag/inveniosoftware/invenio-access.svg
        :target: https://github.com/inveniosoftware/invenio-access/releases

.. image:: https://img.shields.io/pypi/dm/invenio-access.svg
        :target: https://pypi.python.org/pypi/invenio-access

.. image:: https://img.shields.io/github/license/inveniosoftware/invenio-access.svg
        :target: https://github.com/inveniosoftware/invenio-access/blob/master/LICENSE


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
