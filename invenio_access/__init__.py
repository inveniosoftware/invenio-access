# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2022 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Role-based access control for Invenio.

Invenio-Access works together with Invenio-Accounts to provide a full-fledge
authentication and authorization system for Flask and Invenio based on a suite
of existing Flask extensions such as:

- Flask-Security
- Flask-Login
- Flask-Principal
- passlib

Make sure you check out :ref:`concepts` to have a basic understanding of the
entities in the access control system. This part of the usage documentation is
focused on the programmatic APIs and are intended for developers.

Initialization
--------------

Create a Flask application:

>>> import os
>>> db_url = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite://')
>>> from flask import Flask
>>> app = Flask('myapp')
>>> app.config.update({
...     'SQLALCHEMY_DATABASE_URI': db_url,
...     'SQLALCHEMY_TRACK_MODIFICATIONS': False,
...     'SECRET_KEY': 'CHANGE_ME',
... })

Initialize Invenio-Access dependencies, which are Invenio-DB and
Invenio-Accounts, and then Invenio-Access itself:

>>> from invenio_db import InvenioDB
>>> from invenio_accounts import InvenioAccounts
>>> from invenio_access import InvenioAccess
>>> ext_db = InvenioDB(app)
>>> ext_accounts = InvenioAccounts(app)
>>> ext_access = InvenioAccess(app)

The following examples needs to run in a Flask application context, so
let's push one:

>>> app.app_context().push()

Also, for the examples to work we need to create the database and tables (note,
in this example we use an in-memory SQLite database by default):

>>> from invenio_db import db
>>> db.create_all()

Demo data
~~~~~~~~~
Let's also create two initial users and a role:

>>> from invenio_accounts.models import User, Role
>>> alice = User(email='alice@inveniosoftware.org')
>>> bob = User(email='bob@inveniosoftware.org')
>>> admin = Role(name='admin')

Now, assign Alice to the admin role:

>>> admin.users.append(alice)

Last, persist the changees to the database:

>>> db.session.add_all([alice, bob, admin])
>>> db.session.commit()

Protecting resources
--------------------
The basics of protecting a resource involves:

1. Defining one or more actions.
2. Create a permission that requires one or more actions.
3. Check if a permission allows a given identity (i.e. the identity provides
   one more of the required actions).

**1. Define an action**

First, let's start with defining an action (e.g. view an index page in our
module) using the action creation factory:

>>> from invenio_access import action_factory
>>> view_index_action = action_factory('mymodule-index-view')

**2. Create a permission**

Next, we create a permission that requires the just created action:

>>> from invenio_access import Permission
>>> permission = Permission(view_index_action)

**3. Check permission**

In order to check the permission we first need an identity, so let's start out
with an anonymous identity (this happens transparently in the background when
a user login):

>>> from flask_principal import AnonymousIdentity
>>> anonymous = AnonymousIdentity()

Next, we can check if the permission allows the given identity (we will see
in detail below how to use permissions in a view):

>>> permission.allows(anonymous)
False

Granting access
---------------
Checking if the anonymous identity is granted access by a permission is often
not too interesting, so let's grant our admin role access to our action:

>>> from invenio_access.models import ActionRoles, ActionUsers
>>> db.session.add(ActionRoles.allow(view_index_action, role=admin))
>>> db.session.commit()

Next, we need identity instances for our two users (normally you will not have
to worry about this when checking permissions in a view as it is handled
transparently by Flask-Security):

>>> from invenio_access.utils import get_identity
>>> alice_identity = get_identity(alice)
>>> bob_identity = get_identity(bob)

Now that we have the identities, we can check if the permission grants access
to the identities:

>>> permission.allows(alice_identity)
True
>>> permission.allows(bob_identity)
False

Notice, that we granted access to Alice by assigning her the role ``admin``
and granting the role permission on the action.

The Flask-Principal API is pretty rich, and there are multiple other ways
that you can check if a permission grants access to an identity. For instance
below is another example, but please explore the Flask-Principal API
documentation for a full reference:

>>> bob_identity.can(permission)
False

Action parameters
-----------------
Above we created an action that did not take any parameters. These actions are
useful to grant/restrict access to e.g. an entire adminstration interface.
However, in many cases you need object level permissions, in which case you
need to use actions with parameters.

Action with parameters are also created with the
:py:func:`~.factory.action_factory`, but works a bit different as
they take a parameter.

First you create the new action with parameter:

>>> ObjectReadAction = action_factory(
...     'mymodule-object-read', parameter=True)

Everytime you create the action, you also need to create an instance of the
action representing *any* parameter as done like below:

>>> object_read_action_all = ObjectReadAction(None)

**Granting access to actions with parameters**

You grant access to actions with parameters in a similar way as for normal
actions, but you can now grant access to either **all** objects:

>>> db.session.add(ActionRoles.allow(
...     object_read_action_all, role=admin))

Or you can grant access to a **specific** object like this:

>>> db.session.add(ActionUsers.allow(ObjectReadAction(42), user=bob))
>>> db.session.commit()

**Checking permissions for a specific object**

Similar you also create a permission that checks access to a specific object:

>>> permission = Permission(ObjectReadAction(42))
>>> permission.allows(bob_identity)
True
>>> permission.allows(alice_identity)
True

Denying access
--------------
Besides granting access, you can also **deny** access to specific users or
roles. Below for instance we deny access to Alice on the ``view_index_action``.

>>> from invenio_access.models import ActionUsers
>>> db.session.add(ActionUsers.deny(view_index_action, user=alice))
>>> db.session.commit()

When we now check the permission, Alice no longer has access:

>>> permission = Permission(view_index_action)
>>> permission.allows(alice_identity)
False

**Deny takes precedence over allow**

Note, that the deny grant takes precedence over allow grant. Alice was earlier
granted access to the action via her role assignment, however since the deny
grant takes precedence Alice is ultimately denied access.

This is useful if you for instance want to grant access to all objects
*except* one.

Protecting views
----------------
The most common use for permissions is to protect a view. For actions without
parameters you can simply use a decorator for the view:

>>> index_permission = Permission(view_index_action)
>>> @app.route('/')
... @index_permission.require(http_exception=403)
... def index():
...     return 'Protected index page'

Permission factories
~~~~~~~~~~~~~~~~~~~~
In most situations, you however have to deal with object level permissions,
and thus you will have to create the permission on-the-fly via a factory
method. A simple permission factory can look like the one below:

>>> def permission_factory(obj):
...     return Permission(ObjectReadAction(obj['id']))

The factory function simply takes your object and returns a permission for the
specific action. This unfortunately also means that you usually cannot use
the decorator option shown above. Instead you usually have to first fetch your
object from e.g. the database, and then run the permission check:

>>> @app.route('/objects/<int:object_id>')
... def object_view(object_id):
...     with permission_factory({'id': object_id}).require(http_exception=404):
...         return 'Protected index page'

.. note::

    Invenio source code almost exclusively use the permission factory approach
    for protecting views. In addition usually the permission factory is
    configurable so that Invenio instances can fully override the internal
    permission handling.

Security considerations
~~~~~~~~~~~~~~~~~~~~~~~
We can now test the two views via the built-in Flask test client, and see that
anonymous requests are denied in both cases:

>>> with app.test_client() as c:
...     c.get('/')
<WrapperTestResponse streamed [403 FORBIDDEN]>
>>> with app.test_client() as c:
...     c.get('/objects/42')
<WrapperTestResponse streamed [404 NOT FOUND]>

In the two above examples for protecting views, you will notice that in one we
return an HTTP 403 Forbidden error, and in the other we return a HTTP 404 Not
Found error.

In views, you should always make a conscious decision if you should return
401/403 or 404 errors as it has important security considerations.

- **403/401** errors exposes *existence* of an object under a given URL. Hence,
  by using 401/403 errors, the system is "leaking" knowledge that certain
  objects exists in the system. Hence, only use 401/403 errors when this
  behavior is desired. In all other cases use 404 errors.
- **404** errors does not leak any additional information and
  *should be the default error* used when a permission check fails.

Superuser
---------
Invenio-Access provides a way to grant superuser privileges to users or roles
via a superuser action. Granting superuser access to a user implicitly gives
that user access to any action in the system without explicitly having to grant
the action.

For instance, currently Bob does not have permissions on our
``view_index_action``:

>>> permission = Permission(view_index_action)
>>> permission.allows(bob_identity)
False

We can however grant Bob superuser access like this:

>>> from invenio_access.permissions import superuser_access
>>> db.session.add(ActionUsers.allow(superuser_access, user=bob))
>>> db.session.commit()

Now, Bob will have access to the ``view_index_action`` even though we did not
explicitly grant Bob access:

>>> permission.allows(bob_identity)
True

System roles
------------
Invenio-Access, in addition to roles defined by the administrator, provides
also system roles. System roles are defined by the system and automatically
assigned to users.

By default the following system roles exists:

* Any user (guests and autenticated users)
* Authenticated user

System roles works very much like normal roles, so you can e.g. assign actions
to them:

>>> from invenio_access import ActionSystemRoles, any_user
>>> db.session.add(ActionSystemRoles.allow(
...     view_index_action, role=any_user))

In order to test system roles from the shell, we have to manually add the need
into the identity.

>>> anonymous.provides.add(any_user)

Now we can check the permission:

>>> permission = Permission(view_index_action)
>>> permission.allows(anonymous)
True

Creating system roles
~~~~~~~~~~~~~~~~~~~~~
Invenio modules may provide additional system roles. You could, for instance
create a system role that could be used to grant permissions based on IP
address.

First the module should define the system role:

>>> from invenio_access import SystemRoleNeed
>>> campus_user = SystemRoleNeed('campus_user')

Next, connect a receiver to the :py:data:`~identity_loaded`
signal and add the system role need to the identity:

>>> from flask import request
>>> from flask_principal import identity_loaded
>>> @identity_loaded.connect_via(app)
... def on_identity_loaded(sender, identity):
...     if request.remote_addr.startswith('192.168.'):
...         identity.provides.add(campus_user)

Last, you need to register the system role in the Invenio module's entry
points in ``setup.py``:

.. code-block:: python

    entry_points={
        'invenio_access.system_roles': [
            'campus_user'
            ' = mymodule.permissions:campus_user',
        ],
    }

Registering actions
-------------------
All actions that a package provides should be registered in the
``invenio_access.actions`` entry points. This ensures the actions are e.g.
available in the adminstration interface and via the CLI.

Below is an example for of the entry point part of the ``setup.py``:

.. code-block:: python

    entry_points={
        'invenio_access.actions': [
            # Action with parameter
            'object_read_action_all'
            ' = mymodule.permissions:object_read_action_all',
            # Action without parameter
            'view_index_action'
            ' = mymodule.permissions:view_index_action',
        ],
    }

Note that for action with parameters you need point to the import path of the
action representing *any* parameters.

Listing actions
---------------
In order to discover which actions are available in a given installation, one
can retrieve them via:

>>> sorted(app.extensions['invenio-access'].actions.keys())
['admin-access', 'superuser-access']
"""

# Monkey patch Werkzeug 2.1
# Flask-Login uses the safe_str_cmp method which has been removed in Werkzeug
# 2.1. Flask-Login v0.6.0 (yet to be released at the time of writing) fixes the
# issue. Once we depend on Flask-Login v0.6.0 as the minimal version in
# Flask-Security-Invenio/Invenio-Accounts we can remove this patch again.
try:
    # Werkzeug <2.1
    from werkzeug import security

    security.safe_str_cmp
except AttributeError:
    # Werkzeug >=2.1
    import hmac

    from werkzeug import security

    security.safe_str_cmp = hmac.compare_digest

from flask_principal import ActionNeed

from .ext import InvenioAccess
from .factory import action_factory
from .models import ActionRoles, ActionSystemRoles, ActionUsers
from .permissions import (
    ParameterizedActionNeed,
    Permission,
    SystemRoleNeed,
    any_user,
    authenticated_user,
    superuser_access,
)
from .proxies import current_access

__version__ = "1.4.5"

__all__ = (
    "__version__",
    "any_user",
    "authenticated_user",
    "action_factory",
    "current_access",
    "ActionNeed",
    "InvenioAccess",
    "ParameterizedActionNeed",
    "Permission",
    "superuser_access",
    "SystemRoleNeed",
)
