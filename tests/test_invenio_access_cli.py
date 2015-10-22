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

from click.testing import CliRunner
from invenio_accounts.cli import roles_create, users_create

from invenio_access.cli import access


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
        access, ['allow', 'open', '-e', 'unknown'],
        obj=script_info)
    assert result.exit_code != 0


def test_access_cli_allow_action_unknown_role(script_info):
    """Test add action role in access CLI."""
    runner = CliRunner()

    result = runner.invoke(
        access,
        ['allow', 'open', '-r', 'unknown'],
        obj=script_info)
    assert result.exit_code != 0


def test_access_cli_allow_action_user(script_info):
    """Test add action role in access CLI."""
    runner = CliRunner()

    # User creation
    result = runner.invoke(
        users_create,
        ['-e', 'a@example.org', '--password', '123456'],
        obj=script_info
    )
    assert result.exit_code == 0
    result = runner.invoke(
        access, ['allow', 'open', '-e', 'a@example.org'], obj=script_info)
    assert result.exit_code == 0


def test_access_cli_allow_action_role(script_info):
    """Test add action role in access CLI."""
    runner = CliRunner()

    # Rol creation
    result = runner.invoke(
        roles_create,
        ['-n', 'open_role'],
        obj=script_info)
    assert result.exit_code == 0

    result = runner.invoke(
        access,
        ['allow', 'open', '-r', 'open_role'],
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
    assert result.output.find("\nopen\n") != -1
