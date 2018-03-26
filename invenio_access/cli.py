# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Command line interface for Invenio-Access."""

from __future__ import absolute_import, print_function

from functools import wraps

import click
from flask import current_app
from flask.cli import with_appcontext
from invenio_accounts.models import Role, User
from invenio_db import db
from werkzeug.local import LocalProxy

from .models import ActionRoles, ActionUsers

_current_actions = LocalProxy(
    lambda: current_app.extensions['invenio-access'].actions
)
"""Helper proxy to registered actions."""


def lazy_result(f):
    """Decorate function to return LazyProxy."""
    @wraps(f)
    def decorated(ctx, param, value):
        return LocalProxy(lambda: f(ctx, param, value))
    return decorated


@lazy_result
def process_action(ctx, param, value):
    """Return an action if exists."""
    actions = current_app.extensions['invenio-access'].actions
    if value not in actions:
        raise click.BadParameter('Action "%s" is not registered.', value)
    return actions[value]


@lazy_result
def process_email(ctx, param, value):
    """Return an user if it exists."""
    user = User.query.filter(User.email == value).first()
    if not user:
        raise click.BadParameter('User with email \'%s\' not found.', value)
    return user


@lazy_result
def process_role(ctx, param, value):
    """Return a role if it exists."""
    role = Role.query.filter(Role.name == value).first()
    if not role:
        raise click.BadParameter('Role with name \'%s\' not found.', value)
    return role


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
argument_action = click.argument(
    'action', callback=process_action, nargs=1, required=True, metavar='ACTION'
)
argument_user = click.argument(
    'user', callback=process_email, nargs=1, required=True, metavar='EMAIL'
)
argument_role = click.argument(
    'role', callback=process_role, nargs=1, required=True, metavar='ROLE'
)


#
# Access commands
#
@click.group()
def access():
    """Account commands."""


#
# Allow Action
#
@access.group(name='allow', chain=True)
@argument_action
@option_argument
def allow_action(action, argument):
    """Allow action."""


@allow_action.command('user')
@argument_user
def allow_user(user):
    """Allow a user identified by an email address."""
    def processor(action, argument):
        db.session.add(
            ActionUsers.allow(action, argument=argument, user_id=user.id)
        )
    return processor


@allow_action.command('role')
@argument_role
def allow_role(role):
    """Allow a role identified by an email address."""
    def processor(action, argument):
        db.session.add(
            ActionRoles.allow(action, argument=argument, role_id=role.id)
        )
    return processor


@allow_action.resultcallback()
@with_appcontext
def process_allow_action(processors, action, argument):
    """Process allow action."""
    for processor in processors:
        processor(action, argument)
    db.session.commit()


#
# Deny Action
#
@access.group(name='deny', chain=True)
@argument_action
@option_argument
def deny_action(action, argument):
    """Deny actions."""


@deny_action.command('user')
@argument_user
def deny_user(user):
    """Deny a user identified by an email address."""
    def processor(action, argument):
        db.session.add(
            ActionUsers.deny(action, argument=argument, user_id=user.id)
        )
    return processor


@deny_action.command('role')
@argument_role
def deny_role(role):
    """Deny a role identified by an email address."""
    def processor(action, argument):
        db.session.add(
            ActionRoles.deny(action, argument=argument, role_id=role.id)
        )
    return processor


@deny_action.resultcallback()
@with_appcontext
def process_deny_action(processors, action, argument):
    """Process deny action."""
    for processor in processors:
        processor(action, argument)
    db.session.commit()


#
# Remove Action
#
@access.group(name='remove', chain=True)
@argument_action
@option_argument
def remove_action(action, argument):
    """Remove existing action authorization.

    It is possible to specify multible emails and/or roles that
    should be unassigned from the given action.
    """


@remove_action.command('global')
def remove_global():
    """Remove global action rule."""
    def processor(action, argument):
        ActionUsers.query_by_action(action, argument=argument).filter(
            ActionUsers.user_id.is_(None)
        ).delete(synchronize_session=False)
    return processor


@remove_action.command('user')
@argument_user
def remove_user(user):
    """Remove a action for a user."""
    def processor(action, argument):
        ActionUsers.query_by_action(action, argument=argument).filter(
            ActionUsers.user_id == user.id
        ).delete(synchronize_session=False)
    return processor


@remove_action.command('role')
@argument_role
def remove_role(role):
    """Remove a action for a role."""
    def processor(action, argument):
        ActionRoles.query_by_action(action, argument=argument).filter(
            ActionRoles.role_id == role.id
        ).delete(synchronize_session=False)
    return processor


@remove_action.resultcallback()
@with_appcontext
def process_remove_action(processors, action, argument):
    """Process action removals."""
    for processor in processors:
        processor(action, argument)
    db.session.commit()


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
