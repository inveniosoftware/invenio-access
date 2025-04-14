# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Command line interface for Invenio-Access."""

from functools import wraps
from warnings import warn

import click
from flask import current_app
from flask.cli import with_appcontext
from invenio_accounts.models import Role, User
from invenio_db import db
from werkzeug.local import LocalProxy

from .models import ActionRoles, ActionUsers

_current_actions = LocalProxy(lambda: current_app.extensions["invenio-access"].actions)
"""Helper proxy to registered actions."""


def lazy_result(f):
    """Decorate function to return LazyProxy."""

    @wraps(f)
    def decorated(ctx, param, value):
        return LocalProxy(lambda: f(ctx, param, value))

    return decorated


def resultcallback(group):
    """Compatibility layer for Click 7 and 8."""
    if hasattr(group, "result_callback") and group.result_callback is not None:
        decorator = group.result_callback()
    else:
        # Click < 8.0
        decorator = group.resultcallback()
    return decorator


def commit(f):
    """Decorate to commit to database."""

    @wraps(f)
    def decorated(*args, **kwargs):
        ret = f(*args, **kwargs)
        db.session.commit()
        return ret

    return decorated


@lazy_result
def process_action(ctx, param, value):
    """Return an action if exists."""
    actions = current_app.extensions["invenio-access"].actions
    if value not in actions:
        raise click.BadParameter('Action "%s" is not registered.', value)
    return actions[value]


@lazy_result
def process_email(ctx, param, value):
    """Return an user if it exists."""
    user = User.query.filter(User.email == value).first()
    if not user:
        raise click.BadParameter("User with email '%s' not found.", value)
    return user


@lazy_result
def process_role(ctx, param, value):
    """Return a role if it exists."""
    role = Role.query.filter(Role.name == value).first()
    if not role:
        raise click.BadParameter("Role with name '%s' not found.", value)
    return role


option_argument = click.option(
    "-a", "--argument", default=None, help="Value for parameterized action."
)
option_action = click.option("--action", callback=process_action, required=True)
option_user = click.option("--user", callback=process_email, required=True)
option_role = click.option("--role", callback=process_role, required=True)


#
# Access commands
#
@click.group()
@with_appcontext
def access():
    """Account commands."""


@access.command()
@option_user
@option_action
@option_argument
@commit
def allow_action_for_user(user, action, argument):
    """Allow action for user."""
    db.session.add(ActionUsers.allow(action, argument=argument, user_id=user.id))


@access.command()
@option_role
@option_action
@option_argument
@commit
def allow_action_for_role(role, action, argument):
    """Allow action for role."""
    db.session.add(ActionRoles.allow(action, argument=argument, role_id=role.id))


@access.command()
@option_user
@option_action
@option_argument
@commit
def deny_action_for_user(user, action, argument):
    """Deny an action from a user identified by an email address."""
    db.session.add(ActionUsers.deny(action, argument=argument, user_id=user.id))


@access.command()
@option_role
@option_action
@option_argument
@commit
def deny_action_for_role(role, action, argument):
    """Deny an action from role."""
    db.session.add(ActionRoles.deny(action, argument=argument, role_id=role.id))


@access.command()
@option_action
@option_argument
@commit
def remove_action_global(action, argument):
    """Remove global action rule."""
    ActionUsers.query_by_action(action, argument=argument).filter(
        ActionUsers.user_id.is_(None)
    ).delete(synchronize_session=False)


@access.command()
@option_user
@option_action
@option_argument
@commit
def remove_action_from_user(user, action, argument):
    """Remove a action for a user."""
    ActionUsers.query_by_action(action, argument=argument).filter(
        ActionUsers.user_id == user.id
    ).delete(synchronize_session=False)


@access.command()
@option_role
@option_action
@option_argument
@commit
def remove_action_from_role(role, action, argument):
    """Remove a action for a role."""
    ActionRoles.query_by_action(action, argument=argument).filter(
        ActionRoles.role_id == role.id
    ).delete(synchronize_session=False)


@access.command(name="list")
def list_actions():
    """List all registered actions."""
    for name, action in _current_actions.items():
        show_has_argument = "*" if hasattr(action, "argument") else ""
        click.echo(f"{name}:{show_has_argument}")


@access.command(name="show")
@click.option(
    "-e", "--email", multiple=True, default=[], help="User email address(es)."
)
@click.option(
    "-r", "--role", multiple=True, default=[], metavar="ROLE", help="Role name(s)."
)
def show_actions(email, role):
    """Show all assigned actions."""
    if email:
        actions = (
            ActionUsers.query.join(ActionUsers.user).filter(User.email.in_(email)).all()
        )
        for action in actions:
            argument = "" if action.argument is None else action.argument
            exclude = "deny" if action.exclude else "allow"
            color = "red" if action.exclude else "green"
            click.secho(
                f"user:{action.user.email}:{action.action}:{argument}:{exclude}",
                fg=color,
            )

    if role:
        actions = (
            ActionRoles.query.filter(Role.name.in_(role)).join(ActionRoles.role).all()
        )
        for action in actions:
            argument = "" if action.argument is None else action.argument
            exclude = "deny" if action.exclude else "allow"
            color = "red" if action.exclude else "green"
            click.secho(
                f"role:{action.role.name}:{action.action}:{argument}:{exclude}",
                fg=color,
            )


################################
# deprecated implementation
################################

argument_action = click.argument(
    "action", callback=process_action, nargs=1, required=True, metavar="ACTION"
)
argument_user = click.argument(
    "user", callback=process_email, nargs=1, required=True, metavar="EMAIL"
)
argument_role = click.argument(
    "role", callback=process_role, nargs=1, required=True, metavar="ROLE"
)


#
# Allow Action
#
@access.group(name="allow", chain=True)
@argument_action
@option_argument
def allow_action(action, argument):
    """Allow action."""


@allow_action.command("user")
@argument_user
def allow_user(user):
    """Allow a user identified by an email address."""
    warn(
        "Please use the new command allow-action-for-user instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    def processor(action, argument):
        db.session.add(ActionUsers.allow(action, argument=argument, user_id=user.id))

    return processor


@allow_action.command("role")
@argument_role
def allow_role(role):
    """Allow a role identified by an email address."""
    warn(
        "Please use the new command allow-action-for-role instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    def processor(action, argument):
        db.session.add(ActionRoles.allow(action, argument=argument, role_id=role.id))

    return processor


@resultcallback(allow_action)
@with_appcontext
def process_allow_action(processors, action, argument):
    """Process allow action."""
    for processor in processors:
        processor(action, argument)
    db.session.commit()


#
# Deny Action
#
@access.group(name="deny", chain=True)
@argument_action
@option_argument
def deny_action(action, argument):
    """Deny actions."""


@deny_action.command("user")
@argument_user
def deny_user(user):
    """Deny a user identified by an email address."""
    warn(
        "Please use the new command deny-action-for-user instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    def processor(action, argument):
        db.session.add(ActionUsers.deny(action, argument=argument, user_id=user.id))

    return processor


@deny_action.command("role")
@argument_role
def deny_role(role):
    """Deny a role identified by an email address."""
    warn(
        "Please use the new command deny-action-for-role instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    def processor(action, argument):
        db.session.add(ActionRoles.deny(action, argument=argument, role_id=role.id))

    return processor


@resultcallback(deny_action)
@with_appcontext
def process_deny_action(processors, action, argument):
    """Process deny action."""
    for processor in processors:
        processor(action, argument)
    db.session.commit()


#
# Remove Action
#
@access.group(name="remove", chain=True)
@argument_action
@option_argument
def remove_action(action, argument):
    """Remove existing action authorization.

    It is possible to specify multiple emails and/or roles that
    should be unassigned from the given action.
    """


@remove_action.command("global")
def remove_global():
    """Remove global action rule."""
    warn(
        "Please use the new command remove-action-global instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    def processor(action, argument):
        ActionUsers.query_by_action(action, argument=argument).filter(
            ActionUsers.user_id.is_(None)
        ).delete(synchronize_session=False)

    return processor


@remove_action.command("user")
@argument_user
def remove_user(user):
    """Remove a action for a user."""
    warn(
        "Please use the new command remove-action-from-user instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    def processor(action, argument):
        ActionUsers.query_by_action(action, argument=argument).filter(
            ActionUsers.user_id == user.id
        ).delete(synchronize_session=False)

    return processor


@remove_action.command("role")
@argument_role
def remove_role(role):
    """Remove a action for a role."""
    warn(
        "Please use the new command remove-action-from-role instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    def processor(action, argument):
        ActionRoles.query_by_action(action, argument=argument).filter(
            ActionRoles.role_id == role.id
        ).delete(synchronize_session=False)

    return processor


@resultcallback(remove_action)
@with_appcontext
def process_remove_action(processors, action, argument):
    """Process action removals."""
    for processor in processors:
        processor(action, argument)
    db.session.commit()
