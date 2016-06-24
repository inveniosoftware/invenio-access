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


"""Pytest configuration."""

from __future__ import absolute_import, print_function

import os

import pytest
from flask import Flask
from flask.ext.principal import ActionNeed
from flask_babelex import Babel
from flask_mail import Mail
from invenio_accounts import InvenioAccounts
from invenio_db import InvenioDB, db

from invenio_access import InvenioAccess
from invenio_access.permissions import ParameterizedActionNeed

try:
    from flask.cli import ScriptInfo
except ImportError:
    from flask_cli import ScriptInfo


@pytest.fixture()
def app(request):
    """Flask application fixture."""
    app = Flask('testapp')
    app.config.update(
        ACCOUNTS_USE_CELERY=False,
        SECRET_KEY="CHANGE_ME",
        SECURITY_PASSWORD_SALT="CHANGE_ME_ALSO",
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI', 'sqlite:///test.db'),
        TESTING=True,
    )
    if not hasattr(app, 'cli'):
        from flask_cli import FlaskCLI
        FlaskCLI(app)
    Babel(app)
    Mail(app)
    InvenioDB(app)
    InvenioAccounts(app)

    with app.app_context():
        db.create_all()

    def teardown():
        with app.app_context():
            db.drop_all()

    request.addfinalizer(teardown)
    return app


@pytest.fixture()
def script_info(request):
    """Get ScriptInfo object for testing CLI."""
    action_open = ActionNeed('open')
    action_edit = ParameterizedActionNeed('edit', None)

    app_ = app(request)
    ext = InvenioAccess(app_)
    ext.register_action(action_open)
    ext.register_action(action_edit)
    return ScriptInfo(create_app=lambda info: app_)


@pytest.fixture()
def script_info_cli_list(request):
    """Get ScriptInfo object for testing CLI list command."""
    action_open = ActionNeed('open')
    action_edit = ParameterizedActionNeed('edit', None)
    app_ = app(request)
    ext = InvenioAccess(app_)
    ext.register_action(action_open)
    ext.register_action(action_edit)

    return ScriptInfo(create_app=lambda info: app_)
