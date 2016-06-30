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

It aims to make a process of managing access rigths quick and easy while
preventing unwanted visitors performing restricted actions due to system
misconfiguration.

Access module in three points:

- parametrized action needs
- arbitrary combinations of rules for allowing/denying users and/or roles
- support lazy loading of permissions at runtime

Initialization
--------------

First create a Flask application (Flask-CLI is not needed for Flask
version 0.11+):

>>> from flask import Flask
>>> app = Flask('myapp')
>>> app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
>>> if not hasattr(app, 'cli'):
...     from flask_cli import FlaskCLI
...     cli = FlaskCLI(app)

You initialize Access like a normal Flask extension, however Invenio-Access is
dependent on Invenio-DB and Invenio-Accounts so first you need to initialize
these extensions:

>>> from invenio_db import InvenioDB
>>> from invenio_accounts import InvenioAccounts
>>> from invenio_access  import InvenioAccess
>>> ext_db = InvenioDB(app)
>>> ext_accounts = InvenioAccounts(app)
>>> ext_access = InvenioAccess(app)

In order for the following examples to work, you need to work within an
Flask application context so let's push one:

>>> ctx = app.app_context()
>>> ctx.push()

Also, for the examples to work we need to create the database and tables (note,
in this example we use an in-memory SQLite database):

>>> from invenio_db import db
>>> db.create_all()

Dynamic Permissions
-------------------

Dynamic permissions represent needs associated with ``ActionNeed`` or
``ParametrizedActionNeed`` or directly the needs which method is different from
`'action'`. This consequently means that if the action is not attached to
any user or role then it is **allowed** by default.

The permissions are loaded from the database the first time you perform
```needs``` or ```excludes``` in the DynamicPermission object and they are
stored in the instance of DynamicPermission affected to be used in future
calls.

Action Needs
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

Assign actions
~~~~~~~~~~~~~~

You can either assign actions to user or roles. First, you need to have
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
>>> permission_index = DynamicPermission(action_index)
>>> anonymous_identity.can(permission_index)
False
>>> from flask_principal import Identity, RoleNeed, UserNeed
>>> admin_identity = Identity(admin.id)
>>> admin_identity.provides.add(UserNeed(admin.id))
>>> admin_identity.can(permission_index)
True

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
