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

"""Database models for access module."""

from __future__ import absolute_import, print_function

from flask_principal import RoleNeed, UserNeed

from invenio_accounts.models import Role, User

from invenio_db import db


class ActionNeedMixin(object):
    """Define common attributes for Action needs."""

    action = db.Column(db.String(80), primary_key=True)
    """Name of the action."""

    exclude = db.Column(db.Boolean(), nullable=False, default=False,
                        server_default="0")
    """Deny associated objects."""

    argument = db.Column(db.String(255), nullable=True)
    """String value of action argument."""

    @classmethod
    def query_by_action(cls, action):
        """Prepare query object with filtered action."""
        query = cls.query.filter_by(action=action.value)
        if getattr(action, 'argument', None) is not None:
            query = query.filter(db.or_(
                cls.argument == str(action.argument),
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

    user_id = db.Column(db.Integer(), db.ForeignKey(User.id),
                        primary_key=True)

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

    role_id = db.Column(db.Integer(), db.ForeignKey(Role.id),
                        primary_key=True)

    role = db.relationship("Role")

    @property
    def need(self):
        """Return RoleNeed instance."""
        return RoleNeed(self.role.name)
