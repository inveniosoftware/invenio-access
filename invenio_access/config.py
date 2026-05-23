# SPDX-FileCopyrightText: 2016-2018 CERN.
# SPDX-License-Identifier: MIT

"""Default values for access configuration.

.. note::

    By default no caching is enabled. For production instances it is **highly
    advisable** to enable caching as the permission checking is very query
    intensive on the database.
"""

ACCESS_CACHE = None
"""A cache instance or an importable string pointing to the cache instance."""

ACCESS_ACTION_CACHE_PREFIX = "Permission::action::"
"""Prefix for actions cached when used in dynamic permissions."""

ACCESS_LOAD_SYSTEM_ROLE_NEEDS = True
"""Enables the loading of system role needs when users' identity change."""
