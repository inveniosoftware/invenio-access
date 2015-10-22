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


class InvenioAccess(object):
    """Invenio Access extension."""

    def __init__(self, app=None, **kwargs):
        """Extension initialization."""
        self.actions = set()
        self.kwargs = kwargs
        if app:
            self.init_app(app, **kwargs)

    def init_app(self, app, entrypoint_name='invenio_access.actions',
                 **kwargs):
        """Flask application initialization."""
        self.kwargs.update(kwargs)
        app.cli.add_command(access_cli, 'access')
        app.extensions['invenio-access'] = self

        if entrypoint_name:
            for base_entry in pkg_resources.iter_entry_points(entrypoint_name):
                self.register_action(base_entry.load())

    def register_action(self, action):
        """Register an action to be showed in the actions list."""
        self.actions.add(action)
