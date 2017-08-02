# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016, 2017 CERN.
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
from itertools import chain

from flask_principal import ActionNeed, Need, Permission

from .models import ActionRoles, ActionUsers, get_action_cache_key
from .proxies import current_access

_Need = namedtuple('Need', ['method', 'value', 'argument'])

ParameterizedActionNeed = partial(_Need, 'action')

ParameterizedActionNeed.__doc__ = \
    """A need having the method preset to `"action"` and a parameter.

    If it is called with `argument=None` then this need is equivalent
    to ``ActionNeed``.
    """

SystemRoleNeed = partial(Need, 'system_role')
SystemRoleNeed.__doc__ = \
    """A need with the method preset to `"system role"`"""

superuser_access = ActionNeed('superuser-access')
"""SuperUser access allows access to everything on Invenio.

DynamicPermissions allows by default access to SuperUser.
"""

any_user = SystemRoleNeed('any_user')
"""AnyUser system role.

This role is used to assign all possible users (authenticated and guests) to
an action.
"""

authenticated_user = SystemRoleNeed('authenticated_user')
"""AuthenticatedUser system role.

This role is used to assign all authenticated users to an action.
"""


class _P(namedtuple('Permission', ['needs', 'excludes'])):
    """Helper for simple permission updates."""

    def update(self, permission):
        """In-place update of permissions."""
        self.needs.update(permission.needs)
        self.excludes.update(permission.excludes)


class DynamicPermission(Permission):
    """Utility class providing lazy loading of permissions.

    .. warning::

        If ``ActionNeed`` or ``ParameterizedActionNeed`` is not allowed or
        restricted to any user or role then it is **ALLOWED** to anybody.
        This is a major diference to standard ``Permission`` class.
    """

    def __init__(self, *needs):
        r"""Default constructor.

        :param \*needs: A list of need instances.
        """
        self._permissions = None
        self.explicit_needs = set(needs)
        self.explicit_needs.add(superuser_access)

    def _load_permissions(self):
        """Load permissions associated to actions."""
        result = _P(needs=set(), excludes=set())

        for explicit_need in self.explicit_needs:
            if explicit_need.method == 'action':
                action = current_access.get_action_cache(
                    get_action_cache_key(explicit_need.value,
                                         explicit_need.argument
                                         if hasattr(explicit_need, 'argument')
                                         else None)
                )
                if action is None:
                    action = _P(needs=set(), excludes=set())

                    actionsusers = ActionUsers.query_by_action(
                        explicit_need
                    ).all()

                    actionsroles = ActionRoles.query_by_action(
                        explicit_need
                    ).join(
                        ActionRoles.role
                    ).all()

                    for db_action in chain(actionsusers, actionsroles):
                        if db_action.exclude:
                            action.excludes.add(db_action.need)
                        else:
                            action.needs.add(db_action.need)

                    current_access.set_action_cache(
                        get_action_cache_key(explicit_need.value,
                                             explicit_need.argument
                                             if hasattr(explicit_need,
                                                        'argument')
                                             else None),
                        action
                    )
                # in-place update of results
                result.update(action)
            else:
                result.needs.add(explicit_need)
        self._permissions = result

    @property
    def needs(self):
        """Return allowed permissions from database.

        If there is no role or user assigned to an action, everyone is allowed
        to perform that action.

        :returns: A list of need instances.
        """
        self._load_permissions()
        return self._permissions.needs

    @property
    def excludes(self):
        """Return denied permissions from database.

        If there is no role or user assigned to an action, everyone is allowed
        to perform that action.

        :returns: A list of denied permissions.
        """
        self._load_permissions()
        return self._permissions.excludes
