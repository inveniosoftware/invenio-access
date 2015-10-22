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

from invenio_accounts.models import Role, User

from invenio_db import db


class ActionUsers(db.Model):
    """ActionRoles data model.

    It relates an allowd accion with a user.
    """

    __tablename__ = 'access_actionsusers'

    action = db.Column(db.String(80), primary_key=True)

    user_id = db.Column(db.Integer(), db.ForeignKey(User.id), primary_key=True)

    user = db.relationship("User")


class ActionRoles(db.Model):
    """ActionRoles data model.

    It relates an allowd accion with a role.
    """

    __tablename__ = 'access_actionsroles'

    action = db.Column(db.String(80), primary_key=True)

    role_id = db.Column(db.Integer(), db.ForeignKey(Role.id), primary_key=True)

    role = db.relationship("Role")
