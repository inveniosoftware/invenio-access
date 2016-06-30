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

from flask_principal import ActionNeed, RoleNeed, UserNeed
from invenio_accounts.models import Role, User
from invenio_db import db

from invenio_access import InvenioAccess
from invenio_access.models import ActionRoles, ActionUsers
from invenio_access.permissions import DynamicPermission


class FakeIdentity(object):
    """Fake class to test DynamicPermission."""

    def __init__(self, *provides):
        self.provides = set(provides)


def test_invenio_access_permissions_deny(app):
    """User without any provides can't access to a place limited to user 0"""
    InvenioAccess(app)
    with app.test_request_context():
        permission = DynamicPermission(UserNeed(0))

        fake_identity = FakeIdentity()
        assert not permission.allows(fake_identity)


def test_invenio_access_permission_for_users(app):
    """User can access to an action allowed/denied to the user"""
    InvenioAccess(app)
    with app.test_request_context():
        db.session.begin(nested=True)
        superuser = User(email='superuser@inveniosoftware.org')
        user_can_all = User(email='all@inveniosoftware.org')
        user_can_read = User(email='read@inveniosoftware.org')
        user_can_open = User(email='open@inveniosoftware.org')

        db.session.add(superuser)
        db.session.add(user_can_all)
        db.session.add(user_can_read)
        db.session.add(user_can_open)

        db.session.add(ActionUsers(action='superuser-access', user=superuser))

        db.session.add(ActionUsers(action='open', user=user_can_all))
        db.session.add(ActionUsers(action='open', user=user_can_open))

        db.session.add(ActionUsers(action='read', user=user_can_all))
        db.session.add(ActionUsers(action='read', user=user_can_read))
        db.session.commit()

        permission_open = DynamicPermission(ActionNeed('open'))
        permission_read = DynamicPermission(ActionNeed('read'))

        identity_superuser = FakeIdentity(UserNeed(superuser.id))
        identity_all = FakeIdentity(UserNeed(user_can_all.id))
        identity_read = FakeIdentity(UserNeed(user_can_read.id))
        identity_open = FakeIdentity(UserNeed(user_can_open.id))

        assert permission_open.allows(identity_superuser)
        assert permission_read.allows(identity_superuser)

        assert permission_open.allows(identity_all)
        assert permission_read.allows(identity_all)

        assert permission_open.allows(identity_open)
        assert not permission_read.allows(identity_open)

        assert not permission_open.allows(identity_read)
        assert permission_read.allows(identity_read)


def test_invenio_access_permission_for_roles(app):
    """User with a role can access to an action allowed to the role"""
    InvenioAccess(app)
    with app.test_request_context():
        superuser_role = Role(name='superuser')
        admin_role = Role(name='admin')
        reader_role = Role(name='reader')
        opener_role = Role(name='opener')

        db.session.add(superuser_role)
        db.session.add(admin_role)
        db.session.add(reader_role)
        db.session.add(opener_role)

        db.session.add(
            ActionRoles(action='superuser-access', role=superuser_role))

        db.session.add(ActionRoles(action='open', role=admin_role))
        db.session.add(ActionRoles(action='open', role=opener_role))

        db.session.add(ActionRoles(action='read', role=admin_role))
        db.session.add(ActionRoles(action='read', role=reader_role))

        db.session.commit()

    with app.app_context():
        permission_open = DynamicPermission(ActionNeed('open'))
        permission_read = DynamicPermission(ActionNeed('read'))

        identity_superuser = FakeIdentity(RoleNeed('superuser'))
        identity_all = FakeIdentity(RoleNeed('admin'))
        identity_read = FakeIdentity(RoleNeed('reader'))
        identity_open = FakeIdentity(RoleNeed('opener'))

        assert permission_open.allows(identity_superuser)
        assert permission_read.allows(identity_superuser)

        assert permission_open.allows(identity_all)
        assert permission_read.allows(identity_all)

        assert permission_open.allows(identity_open)
        assert not permission_read.allows(identity_open)

        assert not permission_open.allows(identity_read)
        assert permission_read.allows(identity_read)
