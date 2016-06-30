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

import time

from flask_principal import ActionNeed, Need, RoleNeed, UserNeed
from invenio_accounts.models import Role, User
from invenio_db import db
from werkzeug.contrib.cache import RedisCache, SimpleCache

from invenio_access import InvenioAccess, current_access
from invenio_access.models import ActionRoles, ActionUsers
from invenio_access.permissions import DynamicPermission


class FakeIdentity(object):
    """Fake class to test DynamicPermission."""

    def __init__(self, *provides):
        self.provides = provides


def test_invenio_access_permission_cache(app):
    """Caching the user using memory caching."""
    cache = SimpleCache()
    InvenioAccess(app, cache=cache)
    with app.test_request_context():
        user_can_all = User(email='all@inveniosoftware.org')
        user_can_open = User(email='open@inveniosoftware.org')

        db.session.add(user_can_all)
        db.session.add(user_can_open)

        db.session.add(ActionUsers(action='open', user=user_can_all))

        db.session.flush()

        permission_open = DynamicPermission(ActionNeed('open'))

        identity_open = FakeIdentity(UserNeed(user_can_open.id))

        assert not permission_open.allows(identity_open)
        assert current_access.get_action_cache('open') == (
            set([Need(method='id', value=1)]),
            set([])
        )

        db.session.add(ActionUsers(action='open', user=user_can_open))
        db.session.flush()

        permission_open = DynamicPermission(ActionNeed('open'))
        assert permission_open.allows(identity_open)
        assert current_access.get_action_cache('open') == (
            set([Need(method='id', value=1),
                 Need(method='id', value=2)]),
            set([])
        )


def test_invenio_access_permission_cache_redis(app):
    """Caching the user using redis."""
    cache = RedisCache()
    InvenioAccess(app, cache=cache)
    with app.test_request_context():
        user_can_all = User(email='all@inveniosoftware.org')
        user_can_open = User(email='open@inveniosoftware.org')

        db.session.add(user_can_all)
        db.session.add(user_can_open)

        db.session.add(ActionUsers(action='open', user=user_can_all))

        db.session.flush()

        identity_open = FakeIdentity(UserNeed(user_can_open.id))

        permission_open = DynamicPermission(ActionNeed('open'))
        assert not permission_open.allows(identity_open)
        assert current_access.get_action_cache('open') == (
            set([Need(method='id', value=1)]),
            set([])
        )

        db.session.add(ActionUsers(action='open', user=user_can_open))
        db.session.flush()

        permission_open = DynamicPermission(ActionNeed('open'))
        assert permission_open.allows(identity_open)
        assert current_access.get_action_cache('open') == (
            set([Need(method='id', value=1),
                 Need(method='id', value=2)]),
            set([])
        )


def test_intenio_access_cache_performance(app):
    """Performance test simulating 1000 users."""
    InvenioAccess(app, cache=None)
    with app.test_request_context():
        # CDS has (2015-11-19) 74 actions with 414 possible arguments with
        # 49259 users and 307 roles. In this test we are going to divide
        # into 50 and use the next prime number.
        users_number = 991
        actions_users_number = 11
        actions_roles_number = 7

        roles = []
        actions = []
        for i in range(actions_roles_number):
            role = Role(name='role{0}'.format(i))
            roles.append(role)
            db.session.add(role)
            db.session.flush()

            action_role = ActionRoles(
                action='action{0}'.format(
                    str(i % actions_roles_number)),
                role=role)
            actions.append(action_role)
            db.session.add(action_role)
            db.session.flush()

        users = []
        for i in range(users_number):
            user = User(
                email='invenio{0}@inveniosoftware.org'.format(str(i)),
                roles=[roles[i % actions_roles_number]])
            users.append(user)
            db.session.add(user)
            db.session.flush()

            action_user = ActionUsers(action='action{0}'.format(
                str((i % actions_users_number) + actions_roles_number)),
                user=user)
            actions.append(action_user)
            db.session.add(action_user)
            db.session.flush()

        def test_permissions():
            """Iterates over all users checking its permissions."""
            for i in range(users_number):
                identity = FakeIdentity(UserNeed(users[i].id))

                # Allowed permission
                permission_allowed_both = DynamicPermission(
                    ActionNeed('action{0}'.format(
                        (i % actions_users_number) +
                        actions_roles_number)),
                    ActionNeed('action{0}'.format(i % actions_roles_number))
                )
                assert permission_allowed_both.allows(identity)

                # Not allowed action user
                permission_not_allowed_user = DynamicPermission(
                    ActionNeed('action{0}'.format(
                        (i + 1) % actions_users_number +
                        actions_roles_number))
                )
                assert not permission_not_allowed_user.allows(identity)

                # Not allowed action role
                permission_not_allowed_role = DynamicPermission(
                    ActionNeed('action{0}'.format(
                        (i + 1) % actions_roles_number))
                )
                assert not permission_not_allowed_role.allows(identity)

        app.extensions['invenio-access'].cache = None
        start_time_wo_cache = time.time()
        test_permissions()
        end_time_wo_cache = time.time()
        time_wo_cache = end_time_wo_cache - start_time_wo_cache

        app.extensions['invenio-access'].cache = SimpleCache()
        start_time_w_cache = time.time()
        test_permissions()
        end_time_w_cache = time.time()
        time_w_cache = end_time_w_cache - start_time_w_cache

        assert time_wo_cache / time_w_cache > 10


def test_invenio_access_permission_cache_users_updates(app):
    """Testing ActionUsers cache with inserts/updates/deletes."""
    cache = SimpleCache()
    InvenioAccess(app, cache=cache)
    with app.test_request_context():
        # Creation of some data to test.
        user_1 = User(email='user_1@inveniosoftware.org')
        user_2 = User(email='user_2@inveniosoftware.org')
        user_3 = User(email='user_3@inveniosoftware.org')
        user_4 = User(email='user_4@inveniosoftware.org')
        user_5 = User(email='user_5@inveniosoftware.org')

        db.session.add(user_1)
        db.session.add(user_2)
        db.session.add(user_3)
        db.session.add(user_4)
        db.session.add(user_5)

        db.session.add(ActionUsers(action='open', user=user_1))
        db.session.add(ActionUsers(action='write', user=user_4))

        db.session.flush()

        # Creation identities to test.
        identity_user_1 = FakeIdentity(UserNeed(user_1.id))
        identity_user_2 = FakeIdentity(UserNeed(user_2.id))
        identity_user_3 = FakeIdentity(UserNeed(user_3.id))
        identity_user_4 = FakeIdentity(UserNeed(user_4.id))
        identity_user_5 = FakeIdentity(UserNeed(user_5.id))

        # Test if user 1 can open. In this case, the cache should store only
        # this object.
        permission_open = DynamicPermission(ActionNeed('open'))
        assert permission_open.allows(identity_user_1)
        assert current_access.get_action_cache('open') == (
            set([Need(method='id', value=1)]),
            set([])
        )

        # Test if user 4 can write. In this case, the cache should have this
        # new object and the previous one (Open is allowed to user_1)
        permission_write = DynamicPermission(ActionNeed('write'))
        assert permission_write.allows(identity_user_4)
        assert current_access.get_action_cache('write') == (
            set([Need(method='id', value=4)]),
            set([])
        )
        assert current_access.get_action_cache('open') == (
            set([Need(method='id', value=1)]),
            set([])
        )

        # If we add a new user to the action open, the open action in cache
        # should be removed but it should still containing the write entry.
        db.session.add(ActionUsers(action='open', user=user_2))
        db.session.flush()
        assert current_access.get_action_cache('open') is None
        permission_open = DynamicPermission(ActionNeed('open'))
        assert permission_open.allows(identity_user_2)
        assert current_access.get_action_cache('open') == (
            set([Need(method='id', value=1),
                 Need(method='id', value=2)]),
            set([])
        )
        assert current_access.get_action_cache('write') == (
            set([Need(method='id', value=4)]),
            set([])
        )

        # Test if the new user is added to the action 'open'
        permission_write = DynamicPermission(ActionNeed('write'))
        assert permission_write.allows(identity_user_4)
        assert current_access.get_action_cache('open') == (
            set([Need(method='id', value=1),
                 Need(method='id', value=2)]),
            set([])
        )
        assert current_access.get_action_cache('write') == (
            set([Need(method='id', value=4)]),
            set([])
        )

        # If we update an action swapping a user, the cache containing the
        # action, should be removed.
        user_4_action_write = ActionUsers.query.filter(
            ActionUsers.action == 'write' and
            ActionUsers.user == user_4).first()
        user_4_action_write.user = user_3
        db.session.flush()
        assert current_access.get_action_cache('write') is None
        assert current_access.get_action_cache('open') == (
            set([Need(method='id', value=1),
                 Need(method='id', value=2)]),
            set([])
        )

        # Test if the user_3 can now write.
        permission_write = DynamicPermission(ActionNeed('write'))
        assert not permission_write.allows(identity_user_4)
        permission_write = DynamicPermission(ActionNeed('write'))
        assert permission_write.allows(identity_user_3)
        assert current_access.get_action_cache('write') == (
            set([Need(method='id', value=3)]),
            set([])
        )
        assert current_access.get_action_cache('open') == (
            set([Need(method='id', value=1),
                 Need(method='id', value=2)]),
            set([])
        )

        # If we remove a user from an action, the cache should clear the
        # action item.
        user_3_action_write = ActionUsers.query.filter(
            ActionUsers.action == 'write' and
            ActionUsers.user == user_3).first()
        db.session.delete(user_3_action_write)
        db.session.flush()
        assert current_access.get_action_cache('write') is None
        # If no one is allowed to perform an action then everybody is allowed.
        permission_write = DynamicPermission(ActionNeed('write'))
        assert permission_write.allows(identity_user_3)
        assert current_access.get_action_cache('write') == (
            set([]),
            set([])
        )
        db.session.add(ActionUsers(action='write', user=user_5))
        db.session.flush()
        permission_write = DynamicPermission(ActionNeed('write'))
        assert permission_write.allows(identity_user_5)
        permission_write = DynamicPermission(ActionNeed('write'))
        assert not permission_write.allows(identity_user_3)
        assert current_access.get_action_cache('write') == (
            set([Need(method='id', value=5)]),
            set([])
        )
        assert current_access.get_action_cache('open') == (
            set([Need(method='id', value=1),
                 Need(method='id', value=2)]),
            set([])
        )

        # If you update the name of an existing action, the previous action
        # and the new action should be remove from cache.
        permission_write = DynamicPermission(ActionNeed('write'))
        assert permission_write.allows(identity_user_5)
        assert current_access.get_action_cache('write') == (
            set([Need(method='id', value=5)]),
            set([])
        )
        assert current_access.get_action_cache('open') == (
            set([Need(method='id', value=1),
                 Need(method='id', value=2)]),
            set([])
        )
        user_5_action_write = ActionUsers.query.filter(
            ActionUsers.action == 'write' and
            ActionUsers.user == user_5).first()
        user_5_action_write.action = 'open'
        db.session.flush()
        assert current_access.get_action_cache('write') is None
        assert current_access.get_action_cache('open') is None
        permission_open = DynamicPermission(ActionNeed('open'))
        assert permission_open.allows(identity_user_1)
        assert current_access.get_action_cache('open') == (
            set([Need(method='id', value=1),
                 Need(method='id', value=2),
                 Need(method='id', value=5)]),
            set([])
        )
        db.session.add(ActionUsers(action='write', user=user_4))
        permission_write = DynamicPermission(ActionNeed('write'))
        assert not permission_write.allows(identity_user_5)
        assert current_access.get_action_cache('write') == (
            set([Need(method='id', value=4)]),
            set([])
        )


def test_invenio_access_permission_cache_roles_updates(app):
    """Testing ActionRoles cache with inserts/updates/deletes."""
    # This test case is doing the same of user test case but using roles.
    cache = SimpleCache()
    InvenioAccess(app, cache=cache)
    with app.test_request_context():
        # Creation of some data to test.
        role_1 = Role(name='role_1')
        role_2 = Role(name='role_2')
        role_3 = Role(name='role_3')
        role_4 = Role(name='role_4')
        role_5 = Role(name='role_5')

        db.session.add(role_1)
        db.session.add(role_2)
        db.session.add(role_3)
        db.session.add(role_4)
        db.session.add(role_5)

        db.session.add(ActionRoles(action='open', role=role_1))
        db.session.add(ActionRoles(action='write', role=role_4))

        db.session.flush()

        # Creation of identities to test.
        identity_fake_role_1 = FakeIdentity(RoleNeed(role_1.name))
        identity_fake_role_2 = FakeIdentity(RoleNeed(role_2.name))
        identity_fake_role_3 = FakeIdentity(RoleNeed(role_3.name))
        identity_fake_role_4 = FakeIdentity(RoleNeed(role_4.name))
        identity_fake_role_5 = FakeIdentity(RoleNeed(role_5.name))

        # Test if role 1 can open. In this case, the cache should store only
        # this object.
        permission_open = DynamicPermission(ActionNeed('open'))
        assert permission_open.allows(identity_fake_role_1)
        assert current_access.get_action_cache('open') == (
            set([Need(method='role', value=role_1.name)]),
            set([])
        )

        # Test if role 4 can write. In this case, the cache should have this
        # new object and the previous one (Open is allowed to role_1)
        permission_write = DynamicPermission(ActionNeed('write'))
        assert permission_write.allows(identity_fake_role_4)
        assert current_access.get_action_cache('write') == (
            set([Need(method='role', value=role_4.name)]),
            set([])
        )
        assert current_access.get_action_cache('open') == (
            set([Need(method='role', value=role_1.name)]),
            set([])
        )

        # If we add a new role to the action open, the open action in cache
        # should be removed but it should still containing the write entry.
        db.session.add(ActionRoles(action='open', role=role_2))
        db.session.flush()
        assert current_access.get_action_cache('open') is None
        permission_open = DynamicPermission(ActionNeed('open'))
        assert permission_open.allows(identity_fake_role_2)
        assert current_access.get_action_cache('open') == (
            set([Need(method='role', value=role_1.name),
                 Need(method='role', value=role_2.name)]),
            set([])
        )
        assert current_access.get_action_cache('write') == (
            set([Need(method='role', value=role_4.name)]),
            set([])
        )

        # Test if the new role is added to the action 'open'
        permission_write = DynamicPermission(ActionNeed('write'))
        assert permission_write.allows(identity_fake_role_4)
        assert current_access.get_action_cache('open') == (
            set([Need(method='role', value=role_1.name),
                 Need(method='role', value=role_2.name)]),
            set([])
        )
        assert current_access.get_action_cache('write') == (
            set([Need(method='role', value=role_4.name)]),
            set([])
        )

        # If we update an action swapping a role, the cache containing the
        # action, should be removed.
        role_4_action_write = ActionRoles.query.filter(
            ActionRoles.action == 'write' and
            ActionRoles.role == role_4).first()
        role_4_action_write.role = role_3
        db.session.flush()
        assert current_access.get_action_cache('write') is None
        assert current_access.get_action_cache('open') is not None
        assert current_access.get_action_cache('open') == (
            set([Need(method='role', value=role_1.name),
                 Need(method='role', value=role_2.name)]),
            set([])
        )

        # Test if the role_3 can write now.
        permission_write = DynamicPermission(ActionNeed('write'))
        assert not permission_write.allows(identity_fake_role_4)
        permission_write = DynamicPermission(ActionNeed('write'))
        assert permission_write.allows(identity_fake_role_3)
        assert current_access.get_action_cache('write') == (
            set([Need(method='role', value=role_3.name)]),
            set([])
        )
        assert current_access.get_action_cache('open') == (
            set([Need(method='role', value=role_1.name),
                 Need(method='role', value=role_2.name)]),
            set([])
        )

        # If we remove a role from an action, the cache should clear the
        # action item.
        role_3_action_write = ActionRoles.query.filter(
            ActionRoles.action == 'write' and
            ActionRoles.role == role_3).first()
        db.session.delete(role_3_action_write)
        db.session.flush()
        assert current_access.get_action_cache('write') is None
        # If no one is allowed to perform an action then everybody is allowed.
        permission_write = DynamicPermission(ActionNeed('write'))
        assert permission_write.allows(identity_fake_role_3)
        assert current_access.get_action_cache('write') == (
            set([]),
            set([])
        )
        db.session.add(ActionRoles(action='write', role=role_5))
        db.session.flush()
        permission_write = DynamicPermission(ActionNeed('write'))
        assert permission_write.allows(identity_fake_role_5)
        permission_write = DynamicPermission(ActionNeed('write'))
        assert not permission_write.allows(identity_fake_role_3)
        assert current_access.get_action_cache('write') == (
            set([Need(method='role', value=role_5.name)]),
            set([])
        )
        assert current_access.get_action_cache('open') == (
            set([Need(method='role', value=role_1.name),
                 Need(method='role', value=role_2.name)]),
            set([])
        )

        # If you update the name of an existing action, the previous action
        # and the new action should be remove from cache.
        permission_write = DynamicPermission(ActionNeed('write'))
        assert permission_write.allows(identity_fake_role_5)
        assert current_access.get_action_cache('write') == (
            set([Need(method='role', value=role_5.name)]),
            set([])
        )
        assert current_access.get_action_cache('open') == (
            set([Need(method='role', value=role_1.name),
                 Need(method='role', value=role_2.name)]),
            set([])
        )
        role_5_action_write = ActionRoles.query.filter(
            ActionRoles.action == 'write' and
            ActionRoles.role == role_5).first()
        role_5_action_write.action = 'open'
        db.session.flush()
        assert current_access.get_action_cache('write') is None
        assert current_access.get_action_cache('open') is None
        permission_open = DynamicPermission(ActionNeed('open'))
        assert permission_open.allows(identity_fake_role_1)
        assert current_access.get_action_cache('open') == (
            set([Need(method='role', value=role_1.name),
                 Need(method='role', value=role_2.name),
                 Need(method='role', value=role_5.name)]),
            set([])
        )
        db.session.add(ActionRoles(action='write', role=role_4))
        permission_write = DynamicPermission(ActionNeed('write'))
        assert not permission_write.allows(identity_fake_role_5)
        assert current_access.get_action_cache('write') == (
            set([Need(method='role', value=role_4.name)]),
            set([])
        )
