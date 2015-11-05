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

"""Command Line Interface for access."""

from __future__ import absolute_import, print_function

import click
from flask import current_app
from flask_cli import with_appcontext
from invenio_accounts.models import Role, User

from invenio_db import db

from .models import ActionRoles, ActionUsers


def _store_action(action, email, role, exclude=False, argument=None):
    """Store actions."""
    if (len(email) == 0 and len(role) == 0):
        raise click.UsageError('You haven\'t specified any user or role.')

    for email_item in email:
        user = User.query.filter(User.email == email_item).first()
        if not user:
            raise click.BadParameter('User with email \'%s\' not found.',
                                     email_item)
        action_role = ActionUsers(
            action=action, exclude=exclude, argument=argument, user=user
        )
        db.session.add(action_role)

    for role_item in role:
        role = Role.query.filter(Role.name == role_item).first()
        if not role:
            raise click.BadParameter('Role with name \'%s\' not found.',
                                     role_item)
        action_role = ActionRoles(
            action=action, exclude=exclude, argument=argument, role=role
        )
        db.session.add(action_role)
    db.session.commit()


#
# Access commands
#
@click.group()
def access():
    """Account commands."""


@access.command(name='allow')
@click.argument('action')
@click.option('-a', '--argument', default=None)
@click.option('-e', '--email', multiple=True, default=[])
@click.option('-r', '--role', multiple=True, default=[])
@with_appcontext
def allow_action(action, argument, email, role):
    """Allow actions."""
    return _store_action(action, email, role, exclude=False,
                         argument=argument)


@access.command(name='deny')
@click.argument('action')
@click.option('-a', '--argument', default=None)
@click.option('-e', '--email', multiple=True, default=[])
@click.option('-r', '--role', multiple=True, default=[])
@with_appcontext
def deny_action(action, argument, email, role):
    """Deny actions."""
    return _store_action(action, email, role, exclude=True,
                         argument=argument)


@access.command(name='list')
@with_appcontext
def list_actions():
    """List all the actions in the current application."""
    click.echo('Actions used by the current application:')
    actions = current_app.extensions['invenio-access'].actions
    for action in actions:
        click.echo(action.value)
