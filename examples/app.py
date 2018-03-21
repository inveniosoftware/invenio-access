# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Minimal Flask application example for development.

SPHINX-START

First install Invenio-Accces, setup the application and load fixture data by
running:

.. code-block:: console

   $ pip install -e .[all]
   $ cd examples
   $ ./app-setup.sh
   $ ./app-fixtures.sh

You should also have the `Redis` running on your machine. To know how to
install and run `redis`, please refer to the
`redis website <https://redis.io/>`_.

Next, start the development server:

.. code-block:: console

   $ export FLASK_APP=app.py FLASK_DEBUG=1
   $ flask run

and open the example application in your browser:

.. code-block:: console

    $ open http://127.0.0.1:5000/

The login and passwords, as well as the assigned permissions are listed
in ./app-fixtures.sh.

To reset the example application run:

.. code-block:: console

    $ ./app-teardown.sh

SPHINX-END
"""

from __future__ import absolute_import, print_function

import os

import pkg_resources
from flask import Flask, g, render_template
from flask_babelex import Babel
from flask_login import current_user
from flask_mail import Mail
from flask_menu import Menu
from flask_principal import ActionNeed, PermissionDenied, RoleNeed
from invenio_accounts import InvenioAccounts
from invenio_accounts.views import blueprint as blueprint_accounts
from invenio_db import InvenioDB

from invenio_access import InvenioAccess
from invenio_access.permissions import DynamicPermission

# Create Flask application
app = Flask(__name__)
app.config.update({
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
})
app.secret_key = 'ExampleApp'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'SQLALCHEMY_DATABASE_URI', 'sqlite:///instance/test.db'
)
Babel(app)
Mail(app)
Menu(app)
InvenioDB(app)
InvenioAccounts(app)
app.register_blueprint(blueprint_accounts)

access = InvenioAccess(app)

try:
    pkg_resources.get_distribution('invenio_admin')
    from invenio_admin import InvenioAdmin
    InvenioAdmin(app)
except pkg_resources.DistributionNotFound:
    pass

action_open = ActionNeed('open')
access.register_action(action_open)

action_read = ActionNeed('read')
access.register_action(action_read)


@app.errorhandler(PermissionDenied)
def permission_denied_page(error):
    """Show a personalized error message."""
    return "Not Permitted", 403


@app.route("/")
def index():
    """Basic test view."""
    identity = g.identity
    actions = {}
    for action in access.actions.values():
        actions[action.value] = DynamicPermission(action).allows(identity)

    if current_user.is_anonymous:
        return render_template("invenio_access/open.html",
                               actions=actions,
                               identity=identity)
    else:
        return render_template("invenio_access/limited.html",
                               message='',
                               actions=actions,
                               identity=identity)


admin_permission = DynamicPermission(RoleNeed('admin'))


@app.route('/role_admin')
# this decorator limits the access of this view to users with "admin-access"
# permission.
@admin_permission.require()
def role_admin():
    """View only allowed to admin role."""
    identity = g.identity
    actions = {}
    for action in access.actions.values():
        actions[action.value] = DynamicPermission(action).allows(identity)

    message = 'You are opening a page requiring the "admin-access" permission'
    return render_template("invenio_access/limited.html",
                           message=message,
                           actions=actions,
                           identity=identity)


open_permission = DynamicPermission(action_open)


@app.route('/action_open')
@open_permission.require()
def action_open():
    """View only allowed to open action."""
    identity = g.identity
    actions = {}
    for action in access.actions.values():
        actions[action.value] = DynamicPermission(action).allows(identity)

    message = 'You are opening a page requiring the "open" permission'
    return render_template("invenio_access/limited.html",
                           message=message,
                           actions=actions,
                           identity=identity)


read_permission = DynamicPermission(action_read)


@app.route('/action_read')
@read_permission.require()
def action_read():
    """View only allowed to open action."""
    identity = g.identity
    actions = {}
    for action in access.actions.values():
        actions[action.value] = DynamicPermission(action).allows(identity)

    message = 'You are opening a page requiring the "read" permission'
    return render_template("invenio_access/limited.html",
                           message=message,
                           actions=actions,
                           identity=identity)
