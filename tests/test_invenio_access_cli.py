# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Module tests."""

from __future__ import absolute_import, print_function

from click.testing import CliRunner
from flask import g
from flask_principal import ActionNeed
from flask_security.core import _security
from flask_security.utils import login_user
from invenio_accounts.cli import roles_add, roles_create, users_create

from invenio_access.cli import access
from invenio_access.permissions import DynamicPermission, \
    ParameterizedActionNeed


def test_access_cli_allow_action_empty(script_info):
    """Test add action role in access CLI."""
    runner = CliRunner()

    result = runner.invoke(
        access, ['allow', 'open'], obj=script_info)
    assert result.exit_code != 0


def test_access_cli_allow_action_unknown_email(script_info):
    """Test add action role in access CLI."""
    runner = CliRunner()

    result = runner.invoke(
        access, ['allow', 'open', 'user', 'unknown'],
        obj=script_info)
    assert result.exit_code != 0


def test_access_cli_allow_action_unknown_role(script_info):
    """Test add action role in access CLI."""
    runner = CliRunner()

    result = runner.invoke(
        access,
        ['allow', 'open', 'role', 'unknown'],
        obj=script_info)
    assert result.exit_code != 0


def test_access_cli_allow_action_user(script_info):
    """Test add action role in access CLI."""
    runner = CliRunner()

    # User creation
    result = runner.invoke(
        users_create,
        ['a@example.org', '--password', '123456'],
        obj=script_info
    )
    assert result.exit_code == 0
    result = runner.invoke(
        access, ['allow', 'invalid', 'user', 'a@example.org'], obj=script_info)
    assert result.exit_code != 0
    result = runner.invoke(
        access, ['allow', 'open', 'user', 'a@example.org'], obj=script_info)
    assert result.exit_code == 0


def test_any_all_global(script_info):
    """Test any/all/global subcommands."""
    runner = CliRunner()

    result = runner.invoke(access, ['remove', 'open', 'global'],
                           obj=script_info)
    assert result.exit_code == 0

    result = runner.invoke(access, ['remove', 'open', 'global'],
                           obj=script_info)
    assert result.exit_code == 0


def test_access_cli_allow_action_role(script_info):
    """Test add action role in access CLI."""
    runner = CliRunner()

    # Role creation
    result = runner.invoke(
        roles_create,
        ['open_role'],
        obj=script_info)
    assert result.exit_code == 0

    result = runner.invoke(
        access,
        ['allow', 'open', 'role', 'open_role'],
        obj=script_info
    )
    assert result.exit_code == 0


def test_access_cli_deny_action_role(script_info):
    """Test add action role in access CLI."""
    runner = CliRunner()

    # Role creation
    result = runner.invoke(
        roles_create,
        ['edit_role'],
        obj=script_info)
    assert result.exit_code == 0
    result = runner.invoke(
        access,
        ['deny', 'edit', 'role', 'edit_role'],
        obj=script_info
    )
    assert result.exit_code == 0


def test_access_cli_list(script_info_cli_list):
    """Test of list cli command."""
    runner = CliRunner()
    result = runner.invoke(
        access, ['list'],
        obj=script_info_cli_list
    )
    assert result.exit_code == 0
    assert result.output.find("open") != -1


def test_access_matrix(script_info_cli_list):
    """Test of combinations of cli commands."""
    script_info = script_info_cli_list
    runner = CliRunner()

    user_roles = {
        'admin@inveniosoftware.org': ['admin'],
        'admin-edit@inveniosoftware.org': ['admin'],
        'open@inveniosoftware.org': ['opener'],
        'edit@inveniosoftware.org': ['editor'],
        'info@inveniosoftware.org': ['opener'],
    }

    action_roles = {
        'open': ['admin', 'opener'],
        'edit': ['admin', 'editor'],
    }

    for role in {role for roles in user_roles.values() for role in roles}:
        # Role creation
        result = runner.invoke(
            roles_create, [role], obj=script_info
        )
        assert result.exit_code == 0

    for email, roles in user_roles.items():
        result = runner.invoke(
            users_create,
            [email, '--password', '123456', '-a'],
            obj=script_info
        )
        assert result.exit_code == 0

        for role in roles:
            # Role creation
            result = runner.invoke(
                roles_add, [email, role], obj=script_info
            )
            assert result.exit_code == 0

    def role_args(roles):
        """Generate role arguments."""
        for role in roles:
            yield 'role'
            yield role

    for action, roles in action_roles.items():

        result = runner.invoke(
            access,
            ['allow', action] + list(role_args(roles)),
            obj=script_info
        )
        assert result.exit_code == 0

    result = runner.invoke(
        access,
        ['deny', 'edit', 'user', 'admin-edit@inveniosoftware.org'],
        obj=script_info
    )
    assert result.exit_code == 0

    result = runner.invoke(
        access,
        ['allow', '-a', '1', 'edit', 'user', 'info@inveniosoftware.org'],
        obj=script_info
    )
    assert result.exit_code == 0

    permission_open = DynamicPermission(ActionNeed('open'))
    permission_edit = DynamicPermission(ActionNeed('edit'))

    permission_edit_1 = DynamicPermission(ParameterizedActionNeed('edit', 1))
    permission_edit_2 = DynamicPermission(ParameterizedActionNeed('edit', 2))

    user_permissions = {
        'admin@inveniosoftware.org': {
            True: [
                permission_open,
                permission_edit,
                permission_edit_1,
                permission_edit_2,
            ],
        },
        'admin-edit@inveniosoftware.org': {
            True: [permission_open],
            False: [
                permission_edit,
                permission_edit_1,
                permission_edit_2,
            ],
        },
        'open@inveniosoftware.org': {
            True: [permission_open],
            False: [
                permission_edit,
                permission_edit_1,
                permission_edit_2,
            ],
        },
        'edit@inveniosoftware.org': {
            True: [
                permission_edit,
                permission_edit_1,
                permission_edit_2,
            ],
            False: [permission_open],
        },
        'info@inveniosoftware.org': {
            True: [
                permission_open,
                permission_edit_1,
            ],
            False: [
                permission_edit,
                permission_edit_2,
            ],
        },
    }

    for email, permissions in user_permissions.items():
        with script_info.create_app(None).test_request_context():
            user = _security.datastore.find_user(email=email)
            login_user(user)
            identity = g.identity

            for can, actions in permissions.items():
                for action in actions:
                    assert action.allows(identity) == can, identity

    result = runner.invoke(
        access,
        ['remove', 'edit'],
        obj=script_info
    )
    assert result.exit_code == 2

    result = runner.invoke(
        access,
        ['show', '-e', 'admin-edit@inveniosoftware.org'],
        obj=script_info
    )
    assert result.exit_code == 0
    assert 'user:admin-edit@inveniosoftware.org:edit::deny' in result.output

    result = runner.invoke(
        access,
        ['show', '-r', 'editor'],
        obj=script_info
    )
    assert 'role:editor:edit::allow\n' == result.output
    assert result.exit_code == 0

    #
    # Remove all permissions.
    #
    for action, roles in action_roles.items():

        result = runner.invoke(
            access,
            ['remove', action] + list(role_args(roles)),
            obj=script_info
        )
        assert result.exit_code == 0

    result = runner.invoke(
        access,
        ['remove', 'edit', 'user', 'admin-edit@inveniosoftware.org'],
        obj=script_info
    )
    assert result.exit_code == 0

    result = runner.invoke(
        access,
        ['remove', '-a', '1', 'edit', 'user', 'info@inveniosoftware.org'],
        obj=script_info
    )
    assert result.exit_code == 0

    # All authorizations should be removed.
    result = runner.invoke(
        access,
        ['show', '-r', 'admin-edit@inveniosoftware.org'],
        obj=script_info
    )
    assert result.exit_code == 0
    assert result.output == ''
