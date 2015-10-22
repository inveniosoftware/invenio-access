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

"""Invenio module for permissions control."""

from flask.ext.principal import RoleNeed, UserNeed
from flask_principal import Permission

from invenio_access.models import ActionRoles, ActionUsers


class DynamicPermission(Permission):
    """Utility class providing lazy loading of identity provides."""

    def __init__(self, *needs):
        """Default constructor."""
        self.explicit_needs = set(needs)
        self.excludes = set()

    @property
    def needs(self):
        """
        Load allowed actions for the user from database.

        If there is no role or user assigned to an action, everyone is allowed
        too perform that action.
        """
        result = set()

        for explicit_need in self.explicit_needs:
            if explicit_need.method == 'action':
                actionsusers = ActionUsers.query.filter(
                    ActionUsers.action == explicit_need.value).all()
                for actionuser in actionsusers:
                    result.add(UserNeed(actionuser.user_id))

                actionsroles = ActionRoles.query.join(
                    ActionRoles.role).filter(
                    ActionRoles.action == explicit_need.value).all()

                for actionrole in actionsroles:
                    result.add(RoleNeed(actionrole.role.name))
            else:
                result.add(explicit_need)

        return result
