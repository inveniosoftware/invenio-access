# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Permission and action needs for Invenio."""

from collections import namedtuple
from functools import partial
from itertools import chain

from flask_principal import ActionNeed, Identity, Need
from flask_principal import Permission as _Permission

from .models import ActionRoles, ActionSystemRoles, ActionUsers, get_action_cache_key
from .proxies import current_access

_Need = namedtuple("Need", ["method", "value", "argument"])

ParameterizedActionNeed = partial(_Need, "action")

ParameterizedActionNeed.__doc__ = """A need having the method preset to `"action"` and a parameter.

    If it is called with `argument=None` then this need is equivalent
    to ``ActionNeed``.
    """

SystemRoleNeed = partial(Need, "system_role")
SystemRoleNeed.__doc__ = """A need with the method preset to `"system_role"`."""

#
# Need instances
#
superuser_access = ActionNeed("superuser-access")
"""Superuser access aciton which allow access to everything."""

any_user = SystemRoleNeed("any_user")
"""Any user system role.

This role is used to assign all possible users (authenticated and guests)
to an action.
"""

authenticated_user = SystemRoleNeed("authenticated_user")
"""Authenticated user system role.

This role is used to assign all authenticated users to an action.
"""

system_process = SystemRoleNeed("system_process")
"""System role for processes initiated by Invenio itself."""

#
# Identities
#

# the primary requirement for the system user's ID is to be unique
# the IDs of users provided by Invenio-Accounts are positive integers
# the ID of an AnonymousIdentity from Flask-Principle is None
# and the documentation for Flask-Principal makes use of strings for some IDs
system_user_id = "system"
"""The user ID of the system itself, used in its Identity."""

system_identity = Identity(system_user_id)
"""Identity used by system processes."""

system_identity.provides.add(system_process)


class _P(namedtuple("Permission", ["needs", "excludes"])):
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
        self.explicit_excludes = set()

    @staticmethod
    def _cache_key(action_need):
        """Helper method to generate cache key."""
        return get_action_cache_key(
            action_need.value,
            action_need.argument if hasattr(action_need, "argument") else None,
        )

    @staticmethod
    def _split_actionsneeds(needs):
        """Split needs into sets of ActionNeed and any other *Need."""
        action_needs, other_needs = set(), set()
        for need in needs:
            if need.method == "action":
                action_needs.add(need)
            else:
                other_needs.add(need)
        return action_needs, other_needs

    def _load_permissions(self):
        """Load permissions for all needs, expanding actions."""
        result = _P(needs=set(), excludes=set())

        # split ActionNeeds and any other Need in separates Sets
        action_needs, explicit_needs = self._split_actionsneeds(self.explicit_needs)
        action_excludes, explicit_excludes = self._split_actionsneeds(
            self.explicit_excludes
        )

        # add all explicit needs/excludes to the result permissions
        result.needs.update(explicit_needs)
        result.excludes.update(explicit_excludes)

        # expand all ActionNeeds to get all needs/excludes and add them to the
        # result permissions
        for need in action_needs | action_excludes:
            result.update(self._expand_action(need))

        # "allow_by_default = False" means that when needs are empty,
        # then it should deny access.
        # By default, `flask_principal.Permission.allows` will allow access
        # if needs are empty!
        needs_empty = len(result.needs) == 0
        deny_access_when_empty_needs = not self.allow_by_default
        if needs_empty and deny_access_when_empty_needs:
            # Add at least one dummy need so that it will always deny access
            result.needs.update(action_needs)

        self._permissions = result

    def _expand_action(self, explicit_action):
        """Expand action to user/roles needs and excludes."""
        action = current_access.get_action_cache(self._cache_key(explicit_action))
        if action is None:
            action = _P(needs=set(), excludes=set())

            actionsusers = ActionUsers.query_by_action(explicit_action).all()

            actionsroles = (
                ActionRoles.query_by_action(explicit_action)
                .join(ActionRoles.role)
                .all()
            )

            actionssystem = ActionSystemRoles.query_by_action(explicit_action).all()

            for db_action in chain(actionsusers, actionsroles, actionssystem):
                if db_action.exclude:
                    action.excludes.add(db_action.need)
                else:
                    action.needs.add(db_action.need)

            current_access.set_action_cache(self._cache_key(explicit_action), action)
        return action

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
