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


"""Module tests."""

from __future__ import absolute_import, print_function

from flask_principal import ActionNeed, RoleNeed, UserNeed
from invenio_accounts.models import Role, User

from invenio_access.models import ActionRoles, ActionUsers
from invenio_access.permissions import DynamicPermission
from invenio_db import db


class FakeIdentity(object):
    """Fake class to test DynamicPermission."""
    def __init__(self, *provides):
        self.provides = provides


def test_invenio_access_permissions_deny(app):
    """User without any provides can't access to a place limited to user 0"""
    with app.test_request_context():
        permission = DynamicPermission(UserNeed(0))

        fake_identity = FakeIdentity()
        assert not permission.allows(fake_identity)


def test_invenio_access_permission_allowed_action_user(app):
    """User can access to an action allowed to the user"""
    with app.test_request_context():
        email = "test@test.test"
        user = User(id=0, email=email)
        db.session.add(user)
        db.session.commit()
        user = User.query.filter(User.email == "test@test.test").first()
        action_role = ActionUsers(action='open', user_id=user.id)
        db.session.add(action_role)
        db.session.commit()

        permission = DynamicPermission(ActionNeed('open'))

        fake_identity = FakeIdentity(UserNeed(user.id))

        assert permission.allows(fake_identity)


def test_invenio_access_permission_allowed_action_role(app):
    """User with a role can access to an action allowed to the role"""
    with app.test_request_context():
        role_name = 'admin'
        role = Role(id=0, name=role_name)
        db.session.add(role)
        db.session.commit()
        role = Role.query.filter(Role.name == role_name).first()
        action_role = ActionRoles(action='open', role_id=role.id)
        db.session.add(action_role)
        db.session.commit()

        permission = DynamicPermission(ActionNeed('open'))

        fake_identity = FakeIdentity(RoleNeed(role.name))

        assert permission.allows(fake_identity)
