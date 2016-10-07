# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
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


"""Minimal Flask application example for development.

Start redis server.

Install requirements:

.. code-block:: console

   $ pip install -e .[all]
   $ cd examples
   $ ./app-setup.sh
   $ ./app-fixtures.sh

Run the development server:

.. code-block:: console

   $ FLASK_APP=app.py flask run --debugger -p 5000

View the pages using different users:

.. code-block:: console

    $ open http://localhost:5000/
    $ open http://localhost:5000/role_admin
    $ open http://localhost:5000/action_open
    $ open http://localhost:5000/action_read

To be able to uninstall the example app:

.. code-block:: console

    $ ./app-teardown.sh

.. note::

    If you are using an action in your app which does not have any role or user
    assigned, the action will be allowed to perform by everyone (Anonymous
    users included)
"""

from __future__ import absolute_import, print_function

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
app.secret_key = 'ExampleApp'
Babel(app)
Mail(app)
Menu(app)
InvenioDB(app)
InvenioAccounts(app)
app.register_blueprint(blueprint_accounts)

access = InvenioAccess(app)

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
@admin_permission.require()
def role_admin():
    """View only allowed to admin role."""
    identity = g.identity
    actions = {}
    for action in access.actions.values():
        actions[action.value] = DynamicPermission(action).allows(identity)

    message = 'You are opening a page limited to action read'
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

    message = 'You are opening a page limited to action read'
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

    message = 'You are opening a page limited to action read'
    return render_template("invenio_access/limited.html",
                           message=message,
                           actions=actions,
                           identity=identity)
