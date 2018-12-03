# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Permission and action needs for Invenio."""

import warnings
from collections import namedtuple
from functools import partial
from itertools import chain

from flask_principal import ActionNeed, Need
from flask_principal import Permission as _Permission

from .models import ActionRoles, ActionSystemRoles, ActionUsers, \
    get_action_cache_key
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
    """A need with the method preset to `"system_role"`"""

#
# Need instances
#
superuser_access = ActionNeed('superuser-access')
"""Superuser access aciton which allow access to everything."""

any_user = SystemRoleNeed('any_user')
"""Any user system role.

This role is used to assign all possible users (authenticated and guests)
to an action.
"""

authenticated_user = SystemRoleNeed('authenticated_user')
"""Authenticated user system role.

This role is used to assign all authenticated users to an action.
"""


class _P(namedtuple('Permission', ['needs', 'excludes'])):
    """Helper for simple permission updates."""

    def update(self, permission):
        """In-place update of permissions."""
        self.needs.update(permission.needs)
        self.excludes.update(permission.excludes)


class Permission(_Permission):
    """Represents a set of required needs.

    Extends Flask-Principal's :py:class:`flask_principal.Permission` with
    support for loading action grants from the database including caching
    support.

    Essentially the class works as a translation layer that expands action
    needs into a list of user/roles needs. For instance, take the following
    permission:

    .. code-block:: python

        Permission(ActionNeed('my-action'))

    Once the permission is checked with an identity, the class will fetch a
    list of all users and roles that have been granted/denied access to the
    action, and expand the permission into something similar to (depending
    on the state of the database):

    .. code-block:: python

        Permission(UserNeed('1'), RoleNeed('admin'))

    The expansion is cached until the action is modified (e.g. a user is
    granted access to the action). The alternative approach to expanding the
    action need like this class is doing, would be to load the list of allowed
    actions for a user on login and cache the result. However retrieving all
    allowed actions for a  user could results in very large lists, where as
    caching allowed users/roles for an action would usually yield smaller lists
    (especially if roles are used).
    """

    allow_by_default = False
    """If enabled, all permissions are granted when they are not assigned to
    anybody. Disabled by default.
    """

    def __init__(self, *needs):
        r"""Initialize permission.

        :param \*needs: The needs for this permission.
        """
        self._permissions = None
        self.explicit_needs = set(needs)
        self.explicit_needs.add(superuser_access)

    @staticmethod
    def _cache_key(action_need):
        """Helper method to generate cache key."""
        return get_action_cache_key(
            action_need.value,
            action_need.argument if hasattr(action_need, 'argument') else None
        )

    def _load_permissions(self):
        """Load permissions associated to actions."""
        result = _P(needs=set(), excludes=set())
        if not self.allow_by_default:
            result.needs.update(self.explicit_needs)

        for explicit_need in self.explicit_needs:
            if explicit_need.method == 'action':
                action = current_access.get_action_cache(
                    self._cache_key(explicit_need)
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

                    actionssystem = ActionSystemRoles.query_by_action(
                        explicit_need
                    ).all()

                    for db_action in chain(
                            actionsusers, actionsroles, actionssystem):
                        if db_action.exclude:
                            action.excludes.add(db_action.need)
                        else:
                            action.needs.add(db_action.need)

                    current_access.set_action_cache(
                        self._cache_key(explicit_need),
                        action
                    )
                # in-place update of results
                result.update(action)
            elif self.allow_by_default:
                result.needs.add(explicit_need)
        self._permissions = result

    @property
    def needs(self):
        """Return allowed permissions from database.

        :returns: A list of need instances.
        """
        self._load_permissions()
        return self._permissions.needs

    @property
    def excludes(self):
        """Return denied permissions from database.

        :returns: A list of need instances.
        """
        self._load_permissions()
        return self._permissions.excludes


class DynamicPermission(Permission):
    """Represents set of required needs.

    Works like :py:class:`~.Permission` except that any action not
    allowed/restricted to any users, roles or system roles are allowed by
    default instead of restricted.

    .. deprecated:: 1.0.0

        DynamicPermission is deprecated in favor of :py:class:`~.Permission`.

    .. warning::

        This class is going to be removed in a future version.

        The class works significantly different from normal permission class in
        that if ``ActionNeed`` or :py:data:`~.ParameterizedActionNeed` is not
        allowed or restricted to any user or role then it is **ALLOWED** to
        anybody.
    """

    allow_by_default = True

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(DynamicPermission, self).__init__(*args, **kwargs)
        warnings.warn("DynamicPermission is scheduled for removal.",
                      DeprecationWarning)
