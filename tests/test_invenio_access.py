# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Module tests."""

from __future__ import absolute_import, print_function

import pytest
from flask import Flask
from flask_babelex import Babel
from flask_mail import Mail
from flask_principal import ActionNeed
from invenio_accounts import InvenioAccounts
from invenio_db import InvenioDB, db
from invenio_db.utils import drop_alembic_version_table
from mock import patch
from pkg_resources import EntryPoint

from invenio_access import InvenioAccess, current_access
from invenio_access.permissions import SystemRoleNeed


class MockEntryPointAction(EntryPoint):
    """Mocking of entrypoint."""

    def load(self):
        """Mock load entry point."""
        return ActionNeed(self.name)


class MockEntryPointSystemRole(EntryPoint):
    """Mocking of entrypoint."""

    def load(self):
        """Mock load entry point."""
        return SystemRoleNeed(self.name)


def _mock_entry_points(group=None):
    """Mocking funtion of entrypoints."""
    data = {
        'invenio_access.actions': [
            MockEntryPointAction('open', 'demo.actions'),
            MockEntryPointAction('close', 'demo.actions')
        ],
        'invenio_access.system_roles': [
            MockEntryPointSystemRole('any_user', 'demo.specrole'),
            MockEntryPointSystemRole('authenticated_user', 'demo.specrole')
        ],
    }
    names = data.keys() if group is None else [group]
    for key in names:
        for entry_point in data[key]:
            yield entry_point


def test_version():
    """Test version import."""
    from invenio_access import __version__
    assert __version__


def test_init(base_app):
    """Test extension initialization."""
    app = base_app
    ext = InvenioAccess(app)
    assert 'invenio-access' in app.extensions


def test_init_app(base_app):
    """Test extension initialization."""
    app = base_app
    ext = InvenioAccess()
    assert 'invenio-access' not in app.extensions
    ext.init_app(app)
    assert 'invenio-access' in app.extensions


def test_actions(base_app):
    """Test if the actions are registered properly."""
    InvenioAccess(base_app, entry_point_actions=None)
    with base_app.app_context():
        current_access.register_action(ActionNeed('action_a'))
        assert len(current_access.actions) == 1
        current_access.register_action(ActionNeed('action_b'))
        assert len(current_access.actions) == 2


def test_system_roles(base_app):
    """Test if the system roles are registered properly."""
    InvenioAccess(base_app, entry_point_system_roles=None)
    with base_app.app_context():
        current_access.register_system_role(SystemRoleNeed('spn_a'))
        assert len(current_access.system_roles) == 1
        current_access.register_system_role(SystemRoleNeed('spn_b'))
        assert len(current_access.system_roles) == 2


@patch('pkg_resources.iter_entry_points', _mock_entry_points)
def test_entrypoints():
    """Test if the entrypoints are registering actions and roles properly."""
    app = Flask('testapp')
    ext = InvenioAccess(app)
    assert len(ext.actions) == 2
    assert ActionNeed('open') in ext.actions.values()
    assert ActionNeed('close') in ext.actions.values()
    assert len(ext.system_roles) == 2
    assert SystemRoleNeed('any_user') in ext.system_roles.values()
    assert SystemRoleNeed('authenticated_user') in ext.system_roles.values()


def test_alembic(app):
    """Test alembic recipes."""
    ext = app.extensions['invenio-db']

    with app.app_context():
        if db.engine.name == 'sqlite':
            raise pytest.skip('Upgrades are not supported on SQLite.')

        assert not ext.alembic.compare_metadata()
        db.drop_all()
        drop_alembic_version_table()
        ext.alembic.upgrade()

        assert not ext.alembic.compare_metadata()
        ext.alembic.downgrade(target='96e796392533')
        ext.alembic.upgrade()

        assert not ext.alembic.compare_metadata()
