# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Tests for Permission class."""

import pytest
from flask_principal import ActionNeed, Need, RoleNeed, UserNeed
from invenio_accounts.models import Role, User
from invenio_db import db

from invenio_access.models import ActionRoles, ActionSystemRoles, ActionUsers
from invenio_access.permissions import (
    ParameterizedActionNeed,
    Permission,
    any_user,
    authenticated_user,
    superuser_access,
)

# Test cases summary

# List of Need that will be tested:

# UserNeed
# RoleNeed
# ActionNeed
# ParameterizedActionNeed
# SystemRoleNeed

# Test cases (`->` means expand action to a user or a role):

# 1. allow UserNeed
# 2. deny UserNeed
# 3. allow RoleNeed
# 4. deny RoleNeed
# 5. allow UserNeed, RoleNeed
# 6. deny UserNeed, RoleNeed
# 7. allow ActionNeed -> UserNeed
# 8. allow ActionNeed -> RoleNeed
# 9. deny ActionNeed -> UserNeed
# 10. deny ActionNeed -> RoleNeed
# 11. allow ActionNeed -> UserNeed, RoleNeed
# 12. deny ActionNeed -> UserNeed, RoleNeed
# 13. allow/deny ParameterizedActionNeed
# 14. test SystemRoleNeed
# 15. allow_by_default = True/False


class WithUserIdentity(object):
    """Helper class to mock Flask identity and provide needs."""

    def __init__(self, user, *provides):
        self.user = user
        self.id = user.id
        self.provides = set(provides)
        self.provides.add(UserNeed(user.id))
        assert ActionNeed not in self.provides


def get_superuser():
    """Create a superuser user."""
    (superuser,) = create_users("superpowers")
    expand(superuser_access, ("allow", superuser))
    return superuser


def create_users(*names):
    """Helper to create users."""
    users = []
    for name in names:
        user = User(email="{}@inveniosoftware.org".format(name))
        db.session.add(user)
        users.append(user)
    db.session.commit()
    return [WithUserIdentity(user) for user in users]


def create_roles(*names):
    """Helper to create roles."""
    roles = []
    for name in names:
        role = Role(name=name)
        db.session.add(role)
        roles.append(role)
    db.session.commit()
    return roles


def assign_roles(users_roles):
    """Assign roles to users."""
    for user, roles in users_roles.items():
        for role in roles:
            if not isinstance(role, Need):
                role = RoleNeed(role.name)
            user.provides.add(role)


def create_permissions(*permissions):
    """Create permissions with given needs and excludes."""
    _permissions = []
    for _needs in permissions:
        permission = Permission()
        permission.explicit_needs.update(_needs.get("needs", set()))
        permission.explicit_excludes.update(_needs.get("excludes", set()))
        _permissions.append(permission)
    return _permissions


def expand(action_need, *user_or_roles):
    """Expand action to allow/deny users or roles."""
    for user_or_role in user_or_roles:
        allow_deny = user_or_role[0]
        user_role = user_or_role[1]
        argument = user_or_role[2] if len(user_or_role) == 3 else None
        is_user = isinstance(user_role, WithUserIdentity)
        if is_user:
            # User
            kwargs = dict(user=user_role.user)
            method = ActionUsers.allow if allow_deny == "allow" else ActionUsers.deny
        elif isinstance(user_role, Need) and user_role.method == "system_role":
            # SystemRoleNeed
            kwargs = dict(role=user_role)
            method = (
                ActionSystemRoles.allow
                if allow_deny == "allow"
                else ActionSystemRoles.deny
            )
        else:
            # Role
            kwargs = dict(role=user_role)
            method = ActionRoles.allow if allow_deny == "allow" else ActionRoles.deny

        obj = method(action=action_need, argument=argument, **kwargs)
        db.session.add(obj)
    db.session.commit()
    return action_need


def test_allow_by_user_id(access_app):
    """Ensure allow permission by user id."""
    admin, reader = create_users("admin", "reader")

    (permission,) = create_permissions({"needs": {UserNeed(admin.id)}})

    assert permission.allows(admin)
    assert permission.allows(get_superuser())
    assert not permission.allows(reader)


def test_deny_by_user_id(access_app):
    """Ensure deny permission when user is denied."""
    admin, reader = create_users("admin", "reader")

    (permission,) = create_permissions(
        {"excludes": [UserNeed(admin.id), UserNeed(reader.id)]}
    )

    assert not permission.allows(admin)
    assert not permission.allows(reader)
    assert permission.allows(get_superuser())


def test_allow_deny_by_user_id(access_app):
    """Ensure allow/deny permission when same user is allowed and denied."""
    admin, reader = create_users("admin", "reader")

    (permission,) = create_permissions(
        {
            "needs": [UserNeed(admin.id)],
            "excludes": [UserNeed(admin.id), UserNeed(reader.id)],
        }
    )

    # `excludes` prevail over `needs`
    assert not permission.allows(admin)
    assert not permission.allows(reader)
    assert permission.allows(get_superuser())


def test_allow_by_role(access_app):
    """Ensure allow permission by role."""
    admin, reader = create_users("admin", "reader")
    administrators, readers = create_roles("administrators", "readers")
    assign_roles({admin: [administrators], reader: [readers]})

    (permission,) = create_permissions({"needs": [RoleNeed(administrators.name)]})

    assert permission.allows(admin)
    assert not permission.allows(reader)
    assert permission.allows(get_superuser())


def test_deny_by_role(access_app):
    """Ensure deny permission by role."""
    admin, reader = create_users("admin", "reader")
    administrators, readers = create_roles("administrators", "readers")
    assign_roles({admin: [administrators], reader: [readers]})

    (permission,) = create_permissions(
        {
            "needs": [RoleNeed(administrators.name)],
            "excludes": [
                RoleNeed(administrators.name),
                RoleNeed(readers.name),
            ],
        }
    )

    # `excludes` prevail over `needs`
    assert not permission.allows(admin)
    assert not permission.allows(reader)
    assert permission.allows(get_superuser())


def test_allow_by_user_id_and_role(access_app):
    """Ensure allow permission by user id and role."""
    admin, reader = create_users("admin", "reader")
    administrators, readers = create_roles("administrators", "readers")
    assign_roles({admin: [administrators], reader: [readers]})

    (permission,) = create_permissions(
        {"needs": [UserNeed(reader.id), RoleNeed(administrators.name)]}
    )

    assert permission.allows(admin)
    assert permission.allows(reader)
    assert permission.allows(get_superuser())


def test_deny_by_user_id_and_role(access_app):
    """Ensure deny permission by user id and role."""
    admin, reader = create_users("admin", "reader")
    administrators, readers, any_user = create_roles(
        "administrators", "readers", "any_user"
    )
    assign_roles({admin: [administrators, any_user], reader: [readers, any_user]})

    (permission,) = create_permissions(
        {
            "needs": [UserNeed(reader.id), RoleNeed(administrators.name)],
            "excludes": [RoleNeed(any_user.name)],
        }
    )

    assert not permission.allows(admin)
    assert not permission.allows(reader)
    assert permission.allows(get_superuser())


def test_allow_by_action_expands_to_user_id(access_app):
    """Ensure allow permission by action that expands to user id."""
    admin, reader = create_users("admin", "reader")
    administrators, readers = create_roles("administrators", "readers")
    assign_roles({admin: [administrators], reader: [readers]})

    act_access_backoffice = expand(ActionNeed("access-backoffice"), ("allow", admin))
    (permission,) = create_permissions({"needs": [act_access_backoffice]})

    assert permission.allows(admin)
    assert not permission.allows(reader)
    assert permission.allows(get_superuser())


def test_deny_by_action_expands_to_user_id(access_app):
    """Ensure deny permission by action that expands to user id."""
    admin, reader = create_users("admin", "reader")
    administrators, readers = create_roles("administrators", "readers")
    assign_roles({admin: [administrators], reader: [readers]})

    act_access_backoffice = expand(
        ActionNeed("access-backoffice"),
        ("allow", admin),
        ("allow", reader),
        ("deny", admin),
        ("deny", reader),
    )
    (permission,) = create_permissions({"needs": [act_access_backoffice]})

    assert not permission.allows(admin)
    assert not permission.allows(reader)
    assert permission.allows(get_superuser())


def test_allow_by_action_expands_to_role(access_app):
    """Ensure allow permission by action that expands to role."""
    admin, reader = create_users("admin", "reader")
    administrators, readers = create_roles("administrators", "readers")
    assign_roles({admin: [administrators], reader: [readers]})

    act_access_backoffice = expand(
        ActionNeed("access-backoffice"), ("allow", administrators)
    )
    (permission,) = create_permissions({"needs": [act_access_backoffice]})

    assert permission.allows(admin)
    assert not permission.allows(reader)
    assert permission.allows(get_superuser())


def test_deny_by_action_expands_to_role(access_app):
    """Ensure deny permission by action that expands to role."""
    admin, reader = create_users("admin", "reader")
    administrators, readers = create_roles("administrators", "readers")
    assign_roles({admin: [administrators], reader: [readers]})

    act_access_backoffice = expand(
        ActionNeed("access-backoffice"),
        ("allow", administrators),
        ("allow", readers),
        ("deny", administrators),
        ("deny", readers),
    )
    (permission,) = create_permissions({"needs": [act_access_backoffice]})

    assert not permission.allows(admin)
    assert not permission.allows(reader)
    assert permission.allows(get_superuser())


def test_allow_by_action_expands_to_user_id_and_role(access_app):
    """Ensure allow permission by action that expands to user id and role."""
    admin, reader = create_users("admin", "reader")
    administrators, readers = create_roles("administrators", "readers")
    assign_roles({admin: [administrators], reader: [readers]})

    act_access_backoffice = expand(
        ActionNeed("access-backoffice"),
        ("allow", administrators),
        ("allow", reader),
    )
    (permission,) = create_permissions({"needs": [act_access_backoffice]})

    assert permission.allows(admin)
    assert permission.allows(reader)
    assert permission.allows(get_superuser())


def test_deny_by_action_expands_to_user_id_and_role(access_app):
    """Ensure deny permission by action that expands to user id and role."""
    admin, reader = create_users("admin", "reader")
    administrators, readers = create_roles("administrators", "readers")
    assign_roles({admin: [administrators], reader: [readers]})

    act_access_backoffice = expand(
        ActionNeed("access-backoffice"),
        ("allow", administrators),
        ("allow", reader),
        ("deny", administrators),
        ("deny", reader),
    )
    (permission,) = create_permissions({"needs": [act_access_backoffice]})

    assert not permission.allows(admin)
    assert not permission.allows(reader)
    assert permission.allows(get_superuser())


def test_allow_by_action_expands_to_user_id_with_argument(access_app):
    """Ensure allow permission by action that expands to user id + argument."""
    editor1, editor2 = create_users("editor1", "editor2")

    act_edit_record_1 = expand(
        ParameterizedActionNeed("access-edit-record", "1"),
        ("allow", editor1, "1"),
    )
    act_edit_record_2 = expand(
        ParameterizedActionNeed("access-edit-record", "2"),
        ("allow", editor2, "2"),
    )
    permission1, permission2 = create_permissions(
        {"needs": [act_edit_record_1]}, {"needs": [act_edit_record_2]}
    )

    assert permission1.allows(editor1)
    assert not permission1.allows(editor2)
    assert permission2.allows(editor2)
    assert not permission2.allows(editor1)

    superuser = get_superuser()
    assert permission1.allows(superuser)
    assert permission2.allows(superuser)


def test_system_role_name(access_app):
    """Test that ActionSystemRoles fails when created with undeclared names."""
    state = access_app.extensions["invenio-access"]
    db.session.begin(nested=True)
    # Declare a system role.
    state.system_roles = {"any_user": any_user}
    # Create with a declared name.
    ActionSystemRoles(action="read", role_name="any_user")
    # Create with an undeclared name.
    with pytest.raises(AssertionError):
        ActionSystemRoles(action="read", role_name="unknown")


def test_system_roles(access_app):
    """User can access to an action allowed/denied to their system roles."""
    authenticated, anonymous = create_users("authenticated", "anonymous")
    assign_roles({authenticated: [any_user, authenticated_user], anonymous: [any_user]})

    act_read = ActionNeed("read")
    act_write = ActionNeed("write")

    expand(act_write, ("allow", authenticated_user))
    expand(act_read, ("allow", any_user))

    permission_read, permission_write = create_permissions(
        {"needs": [act_read]}, {"needs": [act_write]}
    )

    assert permission_read.allows(anonymous)
    assert permission_read.allows(authenticated)
    assert not permission_write.allows(anonymous)
    assert permission_write.allows(authenticated)

    superuser = get_superuser()
    assert permission_read.allows(superuser)
    assert permission_write.allows(superuser)


def test_allow_by_default(access_app, dynamic_permission):
    """Test that dynamic permissions allows access by default."""
    anonymous, superuser = create_users("anonymous", "superuser")
    act_access_backoffice = ActionNeed("access-backoffice")

    (permission,) = create_permissions({"needs": [act_access_backoffice]})
    dyn_permission = dynamic_permission(act_access_backoffice)

    assert not permission.allows(anonymous)
    assert dyn_permission.allows(anonymous)

    superuser = get_superuser()
    assert permission.allows(superuser)
    assert dyn_permission.allows(superuser)
