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

"""Test for admin view."""

from flask import current_app
from invenio_accounts import InvenioAccounts
from werkzeug.local import LocalProxy

from invenio_access.admin import action_roles_adminview, action_users_adminview

_datastore = LocalProxy(
    lambda: current_app.extensions['security'].datastore
)


def test_admin(app):
    """Test flask-admin interace."""
    assert isinstance(action_roles_adminview, dict)
    assert isinstance(action_users_adminview, dict)

    assert 'model' in action_roles_adminview
    assert 'modelview' in action_roles_adminview
    assert 'model' in action_users_adminview
    assert 'modelview' in action_users_adminview
