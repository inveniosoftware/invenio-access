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

"""Invenio module for common role based access control."""

from __future__ import absolute_import, print_function

from flask import current_app
import pkg_resources
from werkzeug.local import LocalProxy

from .cli import access as access_cli


current_access = LocalProxy(
    lambda: current_app.extensions['invenio-access']
)
"""Helper proxy to access state object."""


class _AccessState(object):
    """Access state storing registered actions."""

    def __init__(self, app, entry_point_group=None, cache=None):
        """Initialize state."""
        self.app = app
        self.actions = {}
        self.cache = cache
        if entry_point_group:
            self.load_entry_point_group(entry_point_group)

    def register_action(self, action):
        """Register an action to be showed in the actions list."""
        assert action.value not in self.actions
        self.actions[action.value] = action

    def load_entry_point_group(self, entry_point_group):
        """Load actions from an entry point group."""
        for ep in pkg_resources.iter_entry_points(group=entry_point_group):
            self.register_action(ep.load())


class InvenioAccess(object):
    """Invenio Access extension."""

    def __init__(self, app=None, **kwargs):
        """Extension initialization."""
        if app:
            self._state = self.init_app(app, **kwargs)

    def init_app(self, app, entry_point_group='invenio_access.actions',
                 **kwargs):
        """Flask application initialization."""
        app.cli.add_command(access_cli, 'access')
        state = _AccessState(app, entry_point_group=entry_point_group,
                             cache=kwargs.get('cache'))
        app.extensions['invenio-access'] = state
        return state

    def __getattr__(self, name):
        """Proxy to state object."""
        return getattr(self._state, name, None)
