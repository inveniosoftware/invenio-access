# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Default values for access configuration.

.. note::

    By default no caching is enabled. For production instances it is **highly
    advisable** to enable caching as the permission checking is very query
    intensive on the database.
"""

ACCESS_CACHE = None
"""A cache instance or an importable string pointing to the cache instance."""

ACCESS_ACTION_CACHE_PREFIX = 'Permission::action::'
"""Prefix for actions cached when used in dynamic permissions."""

ACCESS_LOAD_SYSTEM_ROLE_NEEDS = True
"""Enables the loading of system role needs when users' identity change."""
