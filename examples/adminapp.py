# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
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


"""Minimal Flask application example for admin views.

Create database and tables:

.. code-block:: console

   $ cd examples
   $ flask -a adminapp.py db init
   $ flask -a adminapp.py db create

Create some users:

.. code-block:: console

   $ flask -a adminapp.py users create info@invenio-software.org -a
   $ flask -a adminapp.py users create reader@invenio-software.org -a
   $ flask -a adminapp.py users create editor@invenio-software.org -a
   $ flask -a adminapp.py users create admin@invenio-software.org -a

Run the development server:

.. code-block:: console

   $ flask -a adminapp.py run

"""

from __future__ import absolute_import, print_function

from flask import Flask
from flask_admin import Admin
from flask_babelex import Babel
from flask_cli import FlaskCLI
from flask_mail import Mail
from flask_menu import Menu
from invenio_accounts import InvenioAccounts
from invenio_accounts.views import blueprint
from invenio_admin import InvenioAdmin
from invenio_db import InvenioDB

from invenio_access import InvenioAccess

app = Flask(__name__)
app.secret_key = 'ExampleApp'
FlaskCLI(app)
Babel(app)
Mail(app)
Menu(app)
InvenioDB(app)
InvenioAccounts(app)
access = InvenioAccess(app)

InvenioAdmin(app, permission_factory=lambda x: x,
             view_class_factory=lambda x: x)
