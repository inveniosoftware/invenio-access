# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Database models for access module."""

from __future__ import absolute_import, print_function

from flask_principal import RoleNeed, UserNeed
from invenio_accounts.models import Role, User
from invenio_db import db
from sqlalchemy import UniqueConstraint
from sqlalchemy.event import listen
from sqlalchemy.orm import validates
from sqlalchemy.orm.attributes import get_history

from .proxies import current_access


class ActionNeedMixin(object):
    """Define common attributes for Action needs."""

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    """Primary key. It allows the other fields to be nullable."""

    action = db.Column(db.String(80), index=True)
    """Name of the action."""

    exclude = db.Column(db.Boolean(name='exclude'), nullable=False,
                        default=False, server_default='0')
    """If set to True, deny the action, otherwise allow it."""

    argument = db.Column(db.String(255), nullable=True, index=True)
    """Action argument."""

    @classmethod
    def create(cls, action, **kwargs):
        """Create new database row using the provided action need.

        :param action: An object containing a method equal to ``'action'`` and
            a value.
        :param argument: The action argument. If this parameter is not passed,
            then the ``action.argument`` will be used instead. If the
            ``action.argument`` does not exist, ``None`` will be set as
            argument for the new action need.
        :returns: An :class:`invenio_access.models.ActionNeedMixin` instance.
        """
        assert action.method == 'action'
        argument = kwargs.pop('argument', None) or getattr(
            action, 'argument', None)
        return cls(
            action=action.value,
            argument=argument,
            **kwargs
        )

    @classmethod
    def allow(cls, action, **kwargs):
        """Allow the given action need.

        :param action: The action to allow.
        :returns: A :class:`invenio_access.models.ActionNeedMixin` instance.
        """
        return cls.create(action, exclude=False, **kwargs)

    @classmethod
    def deny(cls, action, **kwargs):
        """Deny the given action need.

        :param action: The action to deny.
        :returns: A :class:`invenio_access.models.ActionNeedMixin` instance.
        """
        return cls.create(action, exclude=True, **kwargs)

    @classmethod
    def query_by_action(cls, action, argument=None):
        """Prepare query object with filtered action.

        :param action: The action to deny.
        :param argument: The action argument. If it's ``None`` then, if exists,
            the ``action.argument`` will be taken. In the worst case will be
            set as ``None``. (Default: ``None``)
        :returns: A query object.
        """
        query = cls.query.filter_by(action=action.value)
        argument = argument or getattr(action, 'argument', None)
        if argument is not None:
            query = query.filter(db.or_(
                cls.argument == str(argument),
                cls.argument.is_(None),
            ))
        else:
            query = query.filter(cls.argument.is_(None))
        return query

    @property
    def need(self):
        """Return the need corresponding to this model instance.

        This is an abstract method and will raise NotImplementedError.
        """
        raise NotImplementedError()  # pragma: no cover


class ActionUsers(ActionNeedMixin, db.Model):
    """ActionUsers data model.

    It relates an allowed action with a user.
    """

    __tablename__ = 'access_actionsusers'

    __table_args__ = (UniqueConstraint(
        'action', 'exclude', 'argument', 'user_id',
        name='access_actionsusers_unique'),
    )

    user_id = db.Column(db.Integer(),
                        db.ForeignKey(User.id, ondelete='CASCADE'),
                        nullable=False, index=True)

    user = db.relationship("User",
                           backref=db.backref("actionusers",
                                              cascade="all, delete-orphan"))

    @property
    def need(self):
        """Return UserNeed instance."""
        return UserNeed(self.user_id)


class ActionRoles(ActionNeedMixin, db.Model):
    """ActionRoles data model.

    It relates an allowed action with a role.
    """

    __tablename__ = 'access_actionsroles'

    __table_args__ = (UniqueConstraint(
        'action', 'exclude', 'argument', 'role_id',
        name='access_actionsroles_unique'),
    )

    role_id = db.Column(db.Integer(),
                        db.ForeignKey(Role.id, ondelete='CASCADE'),
                        nullable=False, index=True)

    role = db.relationship("Role",
                           backref=db.backref("actionusers",
                                              cascade="all, delete-orphan"))

    @property
    def need(self):
        """Return RoleNeed instance."""
        return RoleNeed(self.role.name)


class ActionSystemRoles(ActionNeedMixin, db.Model):
    """ActionSystemRoles data model.

    It relates an allowed action with a predefined role.
    Example: "any user"
    """

    __tablename__ = 'access_actionssystemroles'

    __table_args__ = (UniqueConstraint(
        'action', 'exclude', 'argument', 'role_name',
        name='access_actionssystemroles_unique'),
    )

    role_name = db.Column(db.String(40), nullable=False, index=True)

    @classmethod
    def create(cls, action, **kwargs):
        """Create new database row using the provided action need."""
        role = kwargs.pop('role', None)
        if role:
            assert role.method == 'system_role'
            kwargs['role_name'] = role.value
        return super(ActionSystemRoles, cls).create(action, **kwargs)

    @validates('role_name')
    def validate_role_name(self, key, role_name):
        """Checks that the role name has been registered."""
        assert role_name in current_access.system_roles
        return role_name

    @property
    def need(self):
        """Return the corresponding Need instance."""
        return current_access.system_roles[self.role_name]


def get_action_cache_key(name, argument):
    """Get an action cache key string."""
    tokens = [str(name)]
    if argument:
        tokens.append(str(argument))
    return '::'.join(tokens)


def removed_or_inserted_action(mapper, connection, target):
    """Remove the action from cache when an item is inserted or deleted."""
    current_access.delete_action_cache(get_action_cache_key(target.action,
                                                            target.argument))


def changed_action(mapper, connection, target):
    """Remove the action from cache when an item is updated."""
    action_history = get_history(target, 'action')
    argument_history = get_history(target, 'argument')
    owner_history = get_history(
        target,
        'user' if isinstance(target, ActionUsers) else
        'role' if isinstance(target, ActionRoles) else 'role_name')

    if action_history.has_changes() or argument_history.has_changes() \
       or owner_history.has_changes():
        current_access.delete_action_cache(
            get_action_cache_key(target.action, target.argument))
        current_access.delete_action_cache(
            get_action_cache_key(
                action_history.deleted[0] if action_history.deleted
                else target.action,
                argument_history.deleted[0] if argument_history.deleted
                else target.argument)
        )


listen(ActionUsers, 'after_insert', removed_or_inserted_action)
listen(ActionUsers, 'after_delete', removed_or_inserted_action)
listen(ActionUsers, 'after_update', changed_action)

listen(ActionRoles, 'after_insert', removed_or_inserted_action)
listen(ActionRoles, 'after_delete', removed_or_inserted_action)
listen(ActionRoles, 'after_update', changed_action)

listen(ActionSystemRoles, 'after_insert', removed_or_inserted_action)
listen(ActionSystemRoles, 'after_delete', removed_or_inserted_action)
listen(ActionSystemRoles, 'after_update', changed_action)
