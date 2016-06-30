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

Create database and tables:

.. code-block:: console

   $ cd examples
   $ export FLASK_APP=app.py
   $ flask db init
   $ flask db create

Create some users:

.. code-block:: console

   $ flask users create info@inveniosoftware.org -a
   $ flask users create reader@inveniosoftware.org -a
   $ flask users create editor@inveniosoftware.org -a
   $ flask users create admin@inveniosoftware.org -a

Add a role to a user:

.. code-block:: console

   $ flask roles create -n admin
   $ flask roles add -u info@inveniosoftware.org -r admin
   $ flask roles add -u admin@inveniosoftware.org -r admin

Assign some allowed actions to this users:

.. code-block:: console

   $ flask access allow open -e editor@inveniosoftware.org
   $ flask access deny open -e info@inveniosoftware.org
   $ flask access allow read -e reader@inveniosoftware.org
   $ flask access allow open -r admin
   $ flask access allow read -r admin


Run the development server:

.. code-block:: console

   $ flask run

If you are using an action in your app which does not have any role or user
assigned, the action will be allowed to perform by everyone (Anonymous users
included).

"""

from __future__ import absolute_import, print_function

from flask import Flask, g, render_template
from flask_principal import ActionNeed, RoleNeed
from flask_babelex import Babel
from flask_login import current_user
from flask_mail import Mail
from flask_menu import Menu
from invenio_accounts import InvenioAccounts
from invenio_accounts.views import blueprint
from invenio_db import InvenioDB

from invenio_access import InvenioAccess
from invenio_access.permissions import DynamicPermission

# Create Flask application
app = Flask(__name__)
app.secret_key = 'ExampleApp'
if not hasattr(app, 'cli'):
    from flask_cli import FlaskCLI
    FlaskCLI(app)
Babel(app)
Mail(app)
Menu(app)
InvenioDB(app)
InvenioAccounts(app)
app.register_blueprint(blueprint)

access = InvenioAccess(app)

action_open = ActionNeed('open')
access.register_action(action_open)

action_read = ActionNeed('read')
access.register_action(action_read)


@app.route("/")
def index():
    """Basic test view."""
    identity = g.identity
    actions = {}
    for action in access.actions:
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
    for action in access.actions:
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
    for action in access.actions:
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
    for action in access.actions:
        actions[action.value] = DynamicPermission(action).allows(identity)

    message = 'You are opening a page limited to action read'
    return render_template("invenio_access/limited.html",
                           message=message,
                           actions=actions,
                           identity=identity)
