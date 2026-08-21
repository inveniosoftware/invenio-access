# SPDX-FileCopyrightText: 2017-2018 CERN.
# SPDX-FileCopyrightText: 2026 KTH Royal Institute of Technology.
# SPDX-License-Identifier: MIT

"""Utility functions for Invenio-Access."""

from flask import current_app
from flask_principal import Identity, RoleNeed, UserNeed, identity_changed
from invenio_accounts.proxies import current_datastore

from .permissions import authenticated_user


def get_identity(user):
    """Create an identity for a given user instance.

    Primarily useful for testing.
    """
    identity = Identity(user.id)

    if hasattr(user, "id"):
        identity.provides.add(UserNeed(user.id))

    for role in getattr(user, "roles", []):
        identity.provides.add(RoleNeed(role.id))

    identity.user = user
    return identity


def get_login_identity(id_or_email):
    """Creates an identity as if the user logged in."""
    idty = get_identity(current_datastore.get_user(id_or_email))
    with current_app.test_request_context():
        identity_changed.send(current_app, identity=idty)
        # Needs to be added manually
        idty.provides.add(authenticated_user)
    return idty
