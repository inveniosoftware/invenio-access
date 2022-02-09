# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utility functions for Invenio-Access."""

from flask_principal import Identity, RoleNeed, UserNeed


def get_identity(user):
    """Create an identity for a given user instance.

    Primarily useful for testing.
    """
    id_ = user.get_id()
    identity = Identity(id_)

    if id_ is not None:
        identity.provides.add(UserNeed(id_))

    for role in getattr(user, 'roles', []):
        identity.provides.add(RoleNeed(role.name))

    identity.user = user
    return identity
