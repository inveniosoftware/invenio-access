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

import pkg_resources

from .cli import access as access_cli


class _AccessState(object):
    """Access state storing registered actions."""

    def __init__(self, app, entry_point_group=None, cache=None):
        """Initialize state."""
        self.app = app
        self.actions = {}
        self.cache = cache
        if entry_point_group:
            self.load_entry_point_group(entry_point_group)

    def set_action_cache(self, action_name, data):
        """Store action needs and excludes."""
        if self.cache:
            self.cache.set(
                self.app.config['ACCESS_ACTION_CACHE_PREFIX'] +
                str(action_name), data
            )

    def get_action_cache(self, action_name):
        """Get action needs and excludes from cache."""
        data = None
        if self.cache:
            data = self.cache.get(
                self.app.config['ACCESS_ACTION_CACHE_PREFIX'] +
                str(action_name)
            )
        return data

    def delete_action_cache(self, action_name):
        """Delete action needs and excludes from cache."""
        if self.cache:
            self.cache.delete(
                self.app.config['ACCESS_ACTION_CACHE_PREFIX'] +
                str(action_name)
            )

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
        self.init_config(app)
        app.cli.add_command(access_cli, 'access')
        state = _AccessState(app, entry_point_group=entry_point_group,
                             cache=kwargs.get('cache'))
        app.extensions['invenio-access'] = state
        return state

    def init_config(self, app):
        """Initialize configuration."""
        app.config.setdefault('ACCESS_ACTION_CACHE_PREFIX',
                              'DynamicPermission::action::')

    def __getattr__(self, name):
        """Proxy to state object."""
        return getattr(self._state, name, None)
