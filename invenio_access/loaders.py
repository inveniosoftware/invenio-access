# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""Identity changed loaders."""

from flask_security import current_user

from .permissions import any_user, authenticated_user


def load_permissions_on_identity_loaded(sender, identity):
    """Add system roles "Needs" to users' identities.

    Every user gets the **any_user** Need.
    Authenticated users get in addition the **authenticated_user** Need.
    """
    identity.provides.add(
        any_user
    )
    # if the user is not anonymous
    if current_user.is_authenticated:
        # Add the need provided to authenticated users
        identity.provides.add(
            authenticated_user
        )
