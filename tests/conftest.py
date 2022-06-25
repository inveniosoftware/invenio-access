# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration."""

import os
import warnings

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
from invenio_access.permissions import ParameterizedActionNeed, Permission


@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):
    return compiler.visit_drop_table(element) + " CASCADE"


@compiles(DropConstraint, "postgresql")
def _compile_drop_constraint(element, compiler, **kwargs):
    return compiler.visit_drop_constraint(element) + " CASCADE"


@compiles(DropSequence, "postgresql")
def _compile_drop_sequence(element, compiler, **kwargs):
    return compiler.visit_drop_sequence(element) + " CASCADE"


@pytest.fixture()
def base_app():
    """Flask base application fixture."""
    app_ = Flask("testapp")
    app_.config.update(
        ACCOUNTS_USE_CELERY=False,
        SECRET_KEY="CHANGE_ME",
        SECURITY_PASSWORD_SALT="CHANGE_ME_ALSO",
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            "SQLALCHEMY_DATABASE_URI", "sqlite:///test.db"
        ),
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
def access_app(app):
    """Init InvenioAccess app and return a request context."""
    InvenioAccess(app)
    with app.test_request_context():
        yield app


@pytest.fixture()
def cli_app(app):
    """Get CLI app object for testing CLI."""
    action_open = ActionNeed("open")
    action_edit = ParameterizedActionNeed("edit", None)

    ext = InvenioAccess(app)
    ext.register_action(action_open)
    ext.register_action(action_edit)
    return app


@pytest.fixture()
def dynamic_permission():
    """Dynamic permission fixture."""

    def _get_dynamic_permission(*args):
        """Get dynamic permission."""
        return DynamicPermission(*args)

    return _get_dynamic_permission


class DynamicPermission(Permission):
    """Represents set of required needs.

    Works like :py:class:`~.Permission` except that any action not
    allowed/restricted to any users, roles or system roles are allowed by
    default instead of restricted.

    .. deprecated:: 1.0.0

        DynamicPermission is deprecated in favor of :py:class:`~.Permission`.

    .. warning::

        This class is going to be removed in a future version.

        The class works significantly different from normal permission class in
        that if ``ActionNeed`` or :py:data:`~.ParameterizedActionNeed` is not
        allowed or restricted to any user or role then it is **ALLOWED** to
        anybody.
    """

    allow_by_default = True

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(DynamicPermission, self).__init__(*args, **kwargs)
        warnings.warn("DynamicPermission is scheduled for removal.", DeprecationWarning)
