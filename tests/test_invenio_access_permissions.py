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
from flask_principal import ActionNeed, AnonymousIdentity, RoleNeed, UserNeed
from invenio_accounts.models import Role, User
from invenio_db import db

from invenio_access import InvenioAccess
from invenio_access.models import ActionRoles, ActionSystemRoles, ActionUsers
from invenio_access.permissions import DynamicPermission, \
    ParameterizedActionNeed, Permission, any_user, authenticated_user


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


def test_invenio_access_dynamic_permission(app):
    """DynamicPermission allows by default."""
    fake_identity = FakeIdentity()

    InvenioAccess(app)
    with app.test_request_context():
        db.session.begin(nested=True)
        user = User(email='test@inveniosoftware.org')
        permission = DynamicPermission(ActionNeed('read'))

        # The permission is granted if nobody is assigned the "read" permission
        assert permission.allows(fake_identity)

        # Once the permission is assigned, the need is mandatory
        db.session.add(ActionUsers(action='read', user=user))
        db.session.commit()
        assert not permission.allows(fake_identity)

        fake_identity.provides.add(UserNeed(user.id))
        assert permission.allows(fake_identity)


def test_invenio_access_permission(app):
    """Permission is always denied if not explicitly granted."""
    fake_identity = FakeIdentity()

    InvenioAccess(app)
    with app.test_request_context():
        db.session.begin(nested=True)
        user = User(email='test@inveniosoftware.org')
        permission = Permission(ActionNeed('read'))

        assert not permission.allows(fake_identity)

        db.session.add(ActionUsers(action='read', user=user))
        db.session.commit()

        assert not permission.allows(fake_identity)

        fake_identity.provides.add(UserNeed(user.id))
        assert permission.allows(fake_identity)


def test_invenio_access_system_role_name(app):
    """Check that ActionSystemRoles cannot be created with undeclared names.
    """
    InvenioAccess(app)
    state = app.extensions['invenio-access']
    with app.test_request_context():
        db.session.begin(nested=True)
        # Declare a system role.
        state.system_roles = {'any_user': any_user}
        # Create with a declared name.
        ActionSystemRoles(action='read', role_name='any_user')
        # Create with an undeclared name.
        with pytest.raises(AssertionError):
            ActionSystemRoles(action='read', role_name='unknown')


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

        db.session.add(ActionUsers(action='not_logged', user=user_can_all))

        db.session.commit()

        permission_open = DynamicPermission(ActionNeed('open'))
        permission_read = DynamicPermission(ActionNeed('read'))
        permission_not_logged = DynamicPermission(ActionNeed('not_logged'))

        identity_superuser = FakeIdentity(UserNeed(superuser.id))
        identity_all = FakeIdentity(UserNeed(user_can_all.id))
        identity_read = FakeIdentity(UserNeed(user_can_read.id))
        identity_open = FakeIdentity(UserNeed(user_can_open.id))
        identity_unknown = AnonymousIdentity()

        # global permissions
        assert permission_open.allows(identity_superuser)
        assert permission_read.allows(identity_superuser)

        assert permission_open.allows(identity_all)
        assert permission_read.allows(identity_all)
        assert permission_not_logged.allows(identity_all)

        assert permission_open.allows(identity_open)
        assert not permission_read.allows(identity_open)
        assert not permission_not_logged.allows(identity_open)

        assert not permission_open.allows(identity_read)
        assert permission_read.allows(identity_read)
        assert not permission_not_logged.allows(identity_read)

        assert not permission_open.allows(identity_unknown)
        assert not permission_read.allows(identity_unknown)


def test_invenio_access_argument_permission_for_users(app):
    """User can access to an action allowed/denied with argument to the user"""
    InvenioAccess(app)
    with app.test_request_context():
        db.session.begin(nested=True)
        superuser = User(email='superuser@inveniosoftware.org')
        user_can_all = User(email='all@inveniosoftware.org')
        user_can_argument_dummy = User(email='argumentA@inveniosoftware.org')

        db.session.add(superuser)
        db.session.add(user_can_all)
        db.session.add(user_can_argument_dummy)

        db.session.add(ActionUsers(action='superuser-access', user=superuser))

        db.session.add(ActionUsers(action='argument1',
                                   user=user_can_all))
        db.session.add(ActionUsers(action='argument1',
                                   argument='other',
                                   user=user_can_all))
        db.session.add(ActionUsers(action='argument1',
                                   argument='dummy',
                                   user=user_can_argument_dummy))
        db.session.add(ActionUsers(action='argument2',
                                   argument='other',
                                   user=user_can_all))
        db.session.commit()

        permission_argument1 = DynamicPermission(ActionNeed('argument1'))
        permission_argument1_dummy = DynamicPermission(
            ParameterizedActionNeed('argument1', 'dummy'))
        permission_argument1_other = DynamicPermission(
            ParameterizedActionNeed('argument1', 'other'))
        permission_argument2 = DynamicPermission(ActionNeed('argument2'))
        permission_argument2_dummy = DynamicPermission(
            ParameterizedActionNeed('argument2', 'dummy'))
        permission_argument2_other = DynamicPermission(
            ParameterizedActionNeed('argument2', 'other'))

        identity_superuser = FakeIdentity(UserNeed(superuser.id))
        identity_all = FakeIdentity(UserNeed(user_can_all.id))
        identity_unknown = AnonymousIdentity()
        identity_argument_dummy = FakeIdentity(
            UserNeed(user_can_argument_dummy.id))

        # tests for super user
        assert permission_argument1.allows(identity_superuser)
        assert permission_argument1_dummy.allows(identity_superuser)
        assert permission_argument1_other.allows(identity_superuser)
        assert permission_argument2.allows(identity_superuser)
        assert permission_argument2_dummy.allows(identity_superuser)
        assert permission_argument2_other.allows(identity_superuser)

        # first tests for permissions with argument
        assert permission_argument1.allows(identity_all)
        assert permission_argument1_dummy.allows(identity_all)
        assert permission_argument1_other.allows(identity_all)

        assert not permission_argument1.allows(identity_argument_dummy)
        assert permission_argument1_dummy.allows(identity_argument_dummy)
        assert not permission_argument1_other.allows(identity_argument_dummy)

        assert not permission_argument1.allows(identity_unknown)
        assert not permission_argument1_dummy.allows(identity_unknown)
        assert not permission_argument1_other.allows(identity_unknown)

        # second tests for permissions with arguments
#        assert permission_argument2.allows(identity_all)
#        assert permission_argument2_dummy.allows(identity_all)
        assert permission_argument2_other.allows(identity_all)

#        assert permission_argument2.allows(identity_argument_dummy)
#        assert permission_argument2_dummy.allows(identity_argument_dummy)
        assert not permission_argument2_other.allows(identity_argument_dummy)

#        assert permission_argument2.allows(identity_unknown)
#        assert permission_argument2_dummy.allows(identity_unknown)
        assert not permission_argument2_other.allows(identity_unknown)


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


def test_invenio_access_permission_for_system_roles(app):
    """User can access to an action allowed/denied to their system roles."""
    InvenioAccess(app)
    with app.test_request_context():
        db.session.begin(nested=True)
        user = User(email='user@inveniosoftware.org')

        db.session.add(user)

        db.session.add(ActionSystemRoles.allow(
            action=ActionNeed('open'), role=authenticated_user))
        db.session.add(ActionSystemRoles.allow(
            action=ActionNeed('write'), role_name='any_user'))
        db.session.commit()

        permission_open = DynamicPermission(ActionNeed('open'))
        permission_write = DynamicPermission(ActionNeed('write'))

        identity_anon_user = FakeIdentity(any_user)
        identity_auth_user = FakeIdentity(authenticated_user, any_user)

        assert not permission_open.allows(identity_anon_user)
        assert permission_open.allows(identity_auth_user)

        assert permission_write.allows(identity_anon_user)
        assert permission_write.allows(identity_auth_user)
