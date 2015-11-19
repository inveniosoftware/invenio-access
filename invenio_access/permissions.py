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

"""Invenio module for advanced permission control.

Dynamic permission control is a core feature of *Invenio-Access*
package.  It allows administrator to fine-tune access to various
actions with parameters to a specific user or role.
"""

from collections import namedtuple
from functools import partial

from flask import current_app
from flask_principal import Permission

from invenio_access.models import ActionRoles, ActionUsers

_Need = namedtuple('Need', ['method', 'value', 'argument'])

ParameterizedActionNeed = partial(_Need, 'action')

ParameterizedActionNeed.__doc__ = \
    """A need with the method preset to `"action"` with parameter.

    If it is called with `argument=None` then this need is equivalent
    to ``ActionNeed``.
    """


class DynamicPermission(Permission):
    """Utility class providing lazy loading of permissions.

    .. warning::

        If ``ActionNeed`` or ``ParameterizedActionNeed`` is not allowed or
        restricted to any user or role then it is **ALLOWED** to anybody.
        This is a major diference to standard ``Permission`` class.

    """

    NEEDS = False
    """Key value for associated role and user needs."""

    EXCLUDES = True
    """Key value for excluded role and user needs."""

    def __init__(self, *needs):
        """Default constructor."""
        self._permissions = None
        self.explicit_needs = set(needs)

    def _load_permissions(self):
        """Load permissions associated to actions."""
        result = {
            False: set(),
            True: set(),
        }

        for explicit_need in self.explicit_needs:
            if explicit_need.method == 'action':
                cache = getattr(current_app.extensions['invenio-access'],
                                'cache')
                if cache:
                    cache_key = 'DynamicPermission.action.{0}'.format(
                        explicit_need.value)
                    cached_result = cache.get(cache_key)
                    if cached_result:
                        result[True] |= cached_result[True]
                        result[False] |= cached_result[False]
                        continue

                action = {
                    False: set(),
                    True: set(),
                }

                actionsusers = ActionUsers.query_by_action(
                    explicit_need
                ).all()

                for actionuser in actionsusers:
                    action[actionuser.exclude].add(
                        actionuser.need
                    )

                actionsroles = ActionRoles.query_by_action(
                    explicit_need
                ).join(
                    ActionRoles.role
                ).all()

                for actionrole in actionsroles:
                    action[actionrole.exclude].add(
                        actionrole.need
                    )

                result[True] |= action[True]
                result[False] |= action[False]

                if cache:
                    cache.set(cache_key, action)

            else:
                result[self.NEEDS].add(explicit_need)
        self._permissions = result

    @property
    def needs(self):
        """Return allowed permissions from database.

        If there is no role or user assigned to an action, everyone is allowed
        to perform that action.
        """
        if not self._permissions:
            self._load_permissions()
        return self._permissions[self.NEEDS]

    @property
    def excludes(self):
        """Return denied permissions from database.

        If there is no role or user assigned to an action, everyone is allowed
        to perform that action.
        """
        if not self._permissions:
            self._load_permissions()  # pragma: no cover
        return self._permissions[self.EXCLUDES]
