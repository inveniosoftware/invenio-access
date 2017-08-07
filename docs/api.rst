..
    This file is part of Invenio.
    Copyright (C) 2015, 2016 CERN.

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


API Docs
========

.. automodule:: invenio_access.ext
   :members:

Action factory
--------------

.. automodule:: invenio_access.factory
  :members:

Permissions
-----------

.. autoclass:: invenio_access.permissions.Permission
   :members:

.. autoclass:: invenio_access.permissions.DynamicPermission
   :members:

Needs
-----

.. autodata:: invenio_access.permissions.ParameterizedActionNeed

.. autodata:: invenio_access.permissions.SystemRoleNeed

System roles
------------

.. autodata:: invenio_access.permissions.any_user

.. autodata:: invenio_access.permissions.authenticated_user

.. autodata:: invenio_access.loaders.load_permissions_on_identity_loaded

Actions
-------

.. autodata:: invenio_access.permissions.superuser_access

Models
------

.. automodule:: invenio_access.models
   :members:

Utils
-----

.. automodule:: invenio_access.utils
   :members:

Proxies
-------

.. automodule:: invenio_access.proxies
  :members:

CLI
---

.. automodule:: invenio_access.cli
   :members:

.. autodata:: invenio_access.cli.allow_action

.. autodata:: invenio_access.cli.deny_action

.. autodata:: invenio_access.cli.list_actions
