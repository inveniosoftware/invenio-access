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

"""Database models for access module."""

from __future__ import absolute_import, print_function

from flask_principal import RoleNeed, UserNeed
from invenio_accounts.models import Role, User
from invenio_db import db
from sqlalchemy import UniqueConstraint
from sqlalchemy.event import listen

from .proxies import current_access


class ActionNeedMixin(object):
    """Define common attributes for Action needs."""

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    """Primary key to support nullable fields."""

    action = db.Column(db.String(80), index=True)
    """Name of the action."""

    exclude = db.Column(db.Boolean(), nullable=False,
                        default=False, server_default="0")
    """Deny associated objects."""

    argument = db.Column(db.String(255), nullable=True, index=True)
    """String value of action argument."""

    @classmethod
    def create(cls, action, **kwargs):
        """Create new database instance from action need."""
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
        """Allow given action need."""
        return cls.create(action, exclude=False, **kwargs)

    @classmethod
    def deny(cls, action, **kwargs):
        """Deny usage of given action need."""
        return cls.create(action, exclude=True, **kwargs)

    @classmethod
    def query_by_action(cls, action, argument=None):
        """Prepare query object with filtered action."""
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
        """Abstract need."""
        raise NotImplemented()  # pragma: no cover


class ActionUsers(ActionNeedMixin, db.Model):
    """ActionRoles data model.

    It relates an allowed action with a user.
    """

    __tablename__ = 'access_actionsusers'

    __table_args__ = (UniqueConstraint(
        'action', 'exclude', 'argument', 'user_id',
        name='access_actionsusers_unique'),
    )

    user_id = db.Column(db.Integer(), db.ForeignKey(User.id))

    user = db.relationship("User")

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

    role_id = db.Column(db.Integer(), db.ForeignKey(Role.id), nullable=False)

    role = db.relationship("Role")

    @property
    def need(self):
        """Return RoleNeed instance."""
        return RoleNeed(self.role.name)


def removed_or_inserted_action(mapper, connection, target):
    """Remove the action from cache when an item is inserted or deleted."""
    current_access.delete_action_cache(target.action)


def changed_action_action(target, value, oldvalue, initiator):
    """Remove the action from cache when an action is updated.

    Remove the action from cache when ActionRoles.action or ActionUsers.action
    is updated.
    """
    current_access.delete_action_cache(value)
    current_access.delete_action_cache(oldvalue)


def changed_owner_action(target, value, oldvalue, initiator):
    """Remove the action from cache when the owner is updated.

    Remove the action from cache when ActionRoles.role or ActionUsers.user
    is updated.
    """
    current_access.delete_action_cache(target.action)


listen(ActionUsers, 'after_insert', removed_or_inserted_action)
listen(ActionUsers, 'after_delete', removed_or_inserted_action)
listen(ActionUsers.action, 'set', changed_action_action)
listen(ActionUsers.user, 'set', changed_owner_action)

listen(ActionRoles, 'after_insert', removed_or_inserted_action)
listen(ActionRoles, 'after_delete', removed_or_inserted_action)
listen(ActionRoles.action, 'set', changed_action_action)
listen(ActionRoles.role, 'set', changed_owner_action)
