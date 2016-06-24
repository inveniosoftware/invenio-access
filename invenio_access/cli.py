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

"""Command Line Interface for access."""

from __future__ import absolute_import, print_function

import click
from flask import current_app
from invenio_accounts.models import Role, User
from invenio_db import db
from werkzeug.local import LocalProxy

from .models import ActionRoles, ActionUsers

try:
    from flask.cli import with_appcontext
except ImportError:  # pragma: no cover
    from flask_cli import with_appcontext

_current_actions = LocalProxy(
    lambda: current_app.extensions['invenio-access'].actions
)
"""Helper proxy to registered actions."""


def _store_action(action, email, role, exclude=False, argument=None):
    """Store actions."""
    assert action in _current_actions
    action_need = _current_actions[action]

    if not email and not role:
        raise click.UsageError('You haven\'t specified any user or role.')

    #
    # Assign users
    #
    action_factory = ActionUsers.deny if exclude else ActionUsers.allow

    for email_item in email:
        user = User.query.filter(User.email == email_item).first()
        if not user:
            raise click.BadParameter('User with email \'%s\' not found.',
                                     email_item)

        db.session.add(action_factory(
            action_need, argument=argument, user=user
        ))

    #
    # Assign roles
    #
    action_factory = ActionRoles.deny if exclude else ActionRoles.allow

    for role_item in role:
        role = Role.query.filter(Role.name == role_item).first()
        if not role:
            raise click.BadParameter('Role with name \'%s\' not found.',
                                     role_item)
        db.session.add(action_factory(
            action_need, argument=argument, role=role
        ))

    db.session.commit()


def _remove_action(action, email, role, argument=None):
    """Store actions."""
    assert action in _current_actions
    action_need = _current_actions[action]

    if not email and not role:
        raise click.UsageError('You haven\'t specified any user or role.')

    if email:
        ActionUsers.query_by_action(action_need, argument=argument).filter(
            ActionUsers.user.has(User.email.in_(email))
        ).delete(synchronize_session=False)

    if role:
        ActionRoles.query_by_action(action_need, argument=argument).filter(
            ActionRoles.role.has(Role.name.in_(role))
        ).delete(synchronize_session=False)

    db.session.commit()


option_argument = click.option(
    '-a', '--argument', default=None, metavar='VALUE',
    help='Value for parameterized action.'
)

option_email = click.option(
    '-e', '--email', multiple=True, default=[], metavar='EMAIL',
    help='User email address(es).'
)
option_role = click.option(
    '-r', '--role', multiple=True, default=[], metavar='ROLE',
    help='Role name(s).'
)


#
# Access commands
#
@click.group()
def access():
    """Account commands."""


@access.command(name='allow')
@click.argument('action')
@option_argument
@option_email
@option_role
@with_appcontext
def allow_action(action, argument, email, role):
    """Allow actions."""
    _store_action(action, email, role, exclude=False,
                  argument=argument)


@access.command(name='deny')
@click.argument('action')
@option_argument
@option_email
@option_role
@with_appcontext
def deny_action(action, argument, email, role):
    """Deny actions."""
    _store_action(action, email, role, exclude=True,
                  argument=argument)


@access.command(name='remove')
@click.argument('action')
@option_argument
@option_email
@option_role
@with_appcontext
def remove_action(action, argument, email, role):
    """Remove existing action authorization.

    It is possible to specify multible emails and/or roles that
    should be unassigned from the given action.
    """
    _remove_action(action, email, role, argument=argument)


@access.command(name='list')
@with_appcontext
def list_actions():
    """List all registered actions."""
    for name, action in _current_actions.items():
        click.echo('{0}:{1}'.format(
            name, '*' if hasattr(action, 'argument') else ''
        ))


@access.command(name='show')
@option_email
@option_role
@with_appcontext
def show_actions(email, role):
    """Show all assigned actions."""
    if email:
        actions = ActionUsers.query.join(ActionUsers.user).filter(
            User.email.in_(email)
        ).all()
        for action in actions:
            click.secho('user:{0}:{1}:{2}:{3}'.format(
                action.user.email,
                action.action,
                '' if action.argument is None else action.argument,
                'deny' if action.exclude else 'allow',
            ), fg='red' if action.exclude else 'green')

    if role:
        actions = ActionRoles.query.filter(
            Role.name.in_(role)
        ).join(ActionRoles.role).all()
        for action in actions:
            click.secho('role:{0}:{1}:{2}:{3}'.format(
                action.role.name,
                action.action,
                '' if action.argument is None else action.argument,
                'deny' if action.exclude else 'allow',
            ), fg='red' if action.exclude else 'green')
