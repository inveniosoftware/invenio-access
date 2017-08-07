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


"""Pytest configuration."""

from __future__ import absolute_import, print_function

import os

import pytest
from flask import Flask
from flask.cli import ScriptInfo
from flask_babelex import Babel
from flask_mail import Mail
from flask_principal import ActionNeed, identity_loaded
from invenio_accounts import InvenioAccounts
from invenio_db import InvenioDB, db
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import DropConstraint, DropSequence, DropTable

from invenio_access import InvenioAccess
from invenio_access.loaders import load_permissions_on_identity_loaded
from invenio_access.permissions import ParameterizedActionNeed


@compiles(DropTable, 'postgresql')
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + ' CASCADE'


@compiles(DropConstraint, 'postgresql')
def _compile_drop_constraint(element, compiler, **kwargs):
    return compiler.visit_drop_constraint(element) + ' CASCADE'


@compiles(DropSequence, 'postgresql')
def _compile_drop_sequence(element, compiler, **kwargs):
    return compiler.visit_drop_sequence(element) + ' CASCADE'


@pytest.fixture()
def base_app():
    """Flask base application fixture."""
    app_ = Flask('testapp')
    app_.config.update(
        ACCOUNTS_USE_CELERY=False,
        SECRET_KEY='CHANGE_ME',
        SECURITY_PASSWORD_SALT='CHANGE_ME_ALSO',
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI', 'sqlite:///test.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        TESTING=True,
    )
    Babel(app_)
    Mail(app_)
    InvenioDB(app_)
    InvenioAccounts(app_)
    return app_


@pytest.fixture()
def app(base_app, request):
    """Flask application fixture."""
    with base_app.app_context():
        db.create_all()

    def teardown():

        with base_app.app_context():
            db.drop_all()
            identity_loaded.disconnect(load_permissions_on_identity_loaded)

    request.addfinalizer(teardown)
    return base_app


@pytest.fixture()
def script_info(base_app, request):
    """Get ScriptInfo object for testing CLI."""
    action_open = ActionNeed('open')
    action_edit = ParameterizedActionNeed('edit', None)

    app_ = app(base_app, request)
    ext = InvenioAccess(app_)
    ext.register_action(action_open)
    ext.register_action(action_edit)
    return ScriptInfo(create_app=lambda info: app_)


@pytest.fixture()
def script_info_cli_list(base_app, request):
    """Get ScriptInfo object for testing CLI list command."""
    action_open = ActionNeed('open')
    action_edit = ParameterizedActionNeed('edit', None)
    app_ = app(base_app, request)
    ext = InvenioAccess(app_)
    ext.register_action(action_open)
    ext.register_action(action_edit)

    return ScriptInfo(create_app=lambda info: app_)
