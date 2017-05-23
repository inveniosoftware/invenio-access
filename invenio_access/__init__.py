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

"""Invenio module for common role based access control.

It aims to make the process of managing access rigths quick and easy while
preventing unwanted visitors from performing restricted actions due to system
misconfiguration.

This module uses the Flask-Principal library. You can refer to its
documentation for definitions of "Needs", "Identity" and "Permission" concepts.

Access module in three points:

- parametrized action "Needs"
- arbitrary combinations of rules for allowing/denying users and/or roles
- support lazy loading of permissions at runtime

Initialization
--------------

Create a Flask application:

>>> from flask import Flask
>>> app = Flask('myapp')
>>> app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

Initialize Invenio-Access dependencies, which are Invenio-DB and
Invenio-Accounts, and then Invenio-Access itself:

>>> from invenio_db import InvenioDB
>>> from invenio_accounts import InvenioAccounts
>>> from invenio_access  import InvenioAccess
>>> ext_db = InvenioDB(app)
>>> ext_accounts = InvenioAccounts(app)
>>> ext_access = InvenioAccess(app)

The following examples needs to run in a Flask application context, so
let's push one:

>>> ctx = app.app_context()
>>> ctx.push()

Also, for the examples to work we need to create the database and tables (note,
in this example we use an in-memory SQLite database):

>>> from invenio_db import db
>>> db.create_all()


Dynamic permission control
--------------------------

ActionUsers and ActionRoles
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Flask-Principal provides the ``Need`` concept which reprensents a basic
permission to access a resource, perform an action, etc...

Invenio-Access extends this concept by providing
``ParametrizedActionNeed``. A ``ParametrizedActionNeed`` is used in
order to allow or restrict an action and it has an optional parameter.

Invenio-Access stores two types of ``ParametrizedActionNeeds`` in the database:

- ``ActionUsers``: it allows or denies a user to perform an action.
- ``ActionRoles``: it allows or denies a user role to perform an action.

Actions have a name and can be defined by any module. The optional parameter
can be used as the module sees fit.

DynamicPermission
~~~~~~~~~~~~~~~~~

A ``DynamicPermission`` is based on the Flask-Principle's ``Permission``. It
checks if a user can perform an action by querying the corresponding
``ActionUsers`` and ``ActionRoles`` tables.

The permissions are loaded from the database the first time you perform
```needs``` or ```excludes``` in the ``DynamicPermission`` object and they are
stored in the instance of ``DynamicPermission`` affected to be used in future
calls.

Note that if no ``ActionRoles`` or ``ActionUsers`` exist in the database for
a given action, the action is allowed to every user, including anonymous users.

How it works
~~~~~~~~~~~~

You can start by creating new actions either with or without parameters:

>>> from flask_principal import ActionNeed
>>> from invenio_access import ParameterizedActionNeed
>>> action_index = ActionNeed('index')
>>> action_view_all = ParameterizedActionNeed('view', None)
>>> action_view_1 = ParameterizedActionNeed('view', '1')

If no role or user is attached anybody can perform the action. You can verify
this behavior using following commands.

>>> from flask_principal import AnonymousIdentity
>>> from invenio_access import DynamicPermission, ParameterizedActionNeed
>>> permission_index = DynamicPermission(action_index)
>>> permission_view_all = DynamicPermission(action_view_all)
>>> permission_view_1 = DynamicPermission(action_view_1)
>>> anonymous_identity = AnonymousIdentity()
>>> anonymous_identity.can(permission_index)
True
>>> anonymous_identity.can(permission_view_all)
True
>>> anonymous_identity.can(permission_view_1)
True

If the parameter is set to ``None`` as in this example, the action is allowed
or denied for all possible values. If it is set to a specific value then only
this value is allowed or denied.

Assign actions
~~~~~~~~~~~~~~

Programmatically
++++++++++++++++

You can either assign actions to users or roles. First, you need to have
some users and roles in your database.

>>> from invenio_db import db
>>> from invenio_accounts.models import User, Role
>>> admin = User(email='admin@inveniosoftware.org')
>>> student = User(email='student@inveniosoftware.org')
>>> db.session.begin(nested=True)
<sqlalchemy.orm.session.SessionTransaction object ...
>>> db.session.add(admin)
>>> db.session.add(student)
>>> db.session.commit()

With users created you can allow and deny actions:

>>> from invenio_access.models import ActionUsers
>>> db.session.begin(nested=True)
<sqlalchemy.orm.session.SessionTransaction object ...
>>> db.session.add(ActionUsers.allow(action_index, user=admin))
>>> db.session.commit()

It is then possible to check the permissions:

>>> permission_index = DynamicPermission(action_index)
>>> anonymous_identity.can(permission_index)
False
>>> from flask_principal import Identity, RoleNeed, UserNeed
>>> admin_identity = Identity(admin.id)
>>> admin_identity.provides.add(UserNeed(admin.id))
>>> admin_identity.can(permission_index)
True
>>> student_identity = Identity(student.id)
>>> student_identity.provides.add(UserNeed(student.id))
>>> student_identity.can(permission_index)
False


With the command line interface
+++++++++++++++++++++++++++++++

The permissions can also be assigned using the CLI. For example it is
possible to allow the action ``open``, which is registered in the
example application.

Let's first intialize the example application which we will use.

.. code-block:: console

    $ cd examples
    $ export FLASK_APP=app.py
    $ ./app-setup.sh

Let's create a user.

.. code-block:: console

    $ flask users create admin@inveniosoftware.org -a --password 123456

This is how to allow the action "open" to this user.

.. code-block:: console

    $ flask access allow open user admin@inveniosoftware.org

Run the following command in order to uninstall the example application

.. code-block:: console

    $ ./app-teardown.sh


How to discover existing actions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Modules that intend to implement a given set of actions can register them in
entry points in the corresponding `setup.py`, e.g.

.. code-block:: python

    entry_points={
        'invenio_access.actions': [
            'records_read_all'
            ' = invenio_records.permissions:records_read_all',
            'records_create_all'
            ' = invenio_records.permissions:records_create_all',
            'records_update_all'
            ' = invenio_records.permissions:records_update_all',
            'records_delete_all'
            ' = invenio_records.permissions:records_delete_all',
        ],
    }

In order to discover which actions are available in a given installation one
can retrieve them via:

>>> sorted(app.extensions['invenio-access'].actions.keys())
['admin-access', 'superuser-access']

One can also use CLI to discover registered actions. Here's an example:

.. code-block:: console

    $ cd examples
    $ export FLASK_APP=app.py
    $ flask access list
    read:
    open:
    admin-access:
    superuser-access:
"""

from __future__ import absolute_import, print_function

from .ext import InvenioAccess
from .permissions import DynamicPermission, ParameterizedActionNeed
from .proxies import current_access
from .version import __version__

__all__ = (
    '__version__',
    'current_access',
    'DynamicPermission',
    'InvenioAccess',
    'ParameterizedActionNeed',
)
