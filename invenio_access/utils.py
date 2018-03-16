# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utility functions for Invenio-Access."""

from __future__ import absolute_import, print_function

from flask_principal import Identity, RoleNeed, UserNeed


def get_identity(user):
    """Create an identity for a given user instance.

    Primarily useful for testing.
    """
    identity = Identity(user.id)

    if hasattr(user, 'id'):
        identity.provides.add(UserNeed(user.id))

    for role in getattr(user, 'roles', []):
        identity.provides.add(RoleNeed(role.name))

    identity.user = user
    return identity
