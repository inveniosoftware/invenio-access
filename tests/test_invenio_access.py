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


"""Module tests."""

from __future__ import absolute_import, print_function

from flask import Flask
from flask_babelex import Babel
from flask_mail import Mail
from flask_principal import ActionNeed
from invenio_accounts import InvenioAccounts
from invenio_db import InvenioDB
from mock import patch
from pkg_resources import EntryPoint

from invenio_access import InvenioAccess, current_access


class MockEntryPoint(EntryPoint):
    """Mocking of entrypoint."""

    def load(self):
        """Mock load entry point."""
        return ActionNeed(self.name)


def _mock_entry_points(group=None):
    """Mocking funtion of entrypoints."""
    data = {
        'invenio_access.actions': [MockEntryPoint('open',
                                                  'demo.actions'),
                                   MockEntryPoint('close',
                                                  'demo.actions')],
    }
    names = data.keys() if group is None else [group]
    for key in names:
        for entry_point in data[key]:
            yield entry_point


def test_version():
    """Test version import."""
    from invenio_access import __version__
    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask('testapp')
    if not hasattr(app, 'cli'):
        from flask_cli import FlaskCLI
        FlaskCLI(app)
    Babel(app)
    Mail(app)
    InvenioDB(app)
    InvenioAccounts(app)
    ext = InvenioAccess(app)
    assert 'invenio-access' in app.extensions

    app = Flask('testapp')
    if not hasattr(app, 'cli'):
        from flask_cli import FlaskCLI
        FlaskCLI(app)
    Babel(app)
    Mail(app)
    InvenioDB(app)
    InvenioAccounts(app)
    ext = InvenioAccess()
    assert 'invenio-access' not in app.extensions
    ext.init_app(app)
    assert 'invenio-access' in app.extensions


def test_actions():
    """Test if the actions are registered properly."""
    app = Flask('testapp')
    if not hasattr(app, 'cli'):
        from flask_cli import FlaskCLI
        FlaskCLI(app)
    Babel(app)
    Mail(app)
    InvenioDB(app)
    InvenioAccounts(app)
    InvenioAccess(app, entry_point_group=None)
    with app.app_context():
        current_access.register_action(ActionNeed('action_a'))
        assert len(current_access.actions) == 1
        current_access.register_action(ActionNeed('action_b'))
        assert len(current_access.actions) == 2


@patch('pkg_resources.iter_entry_points', _mock_entry_points)
def test_actions_entrypoint():
    """Test if the entrypoint is registering actions properly."""
    app = Flask('testapp')
    if not hasattr(app, 'cli'):
        from flask_cli import FlaskCLI
        FlaskCLI(app)
    ext = InvenioAccess(app)
    assert len(ext.actions) == 2
    assert ActionNeed('open') in ext.actions.values()
    assert ActionNeed('close') in ext.actions.values()
