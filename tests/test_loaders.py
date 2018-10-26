# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test Indentity loaders."""

from flask import current_app, g
from flask_principal import AnonymousIdentity, UserNeed, identity_changed, \
    identity_loaded
from flask_security.utils import login_user, logout_user
from invenio_accounts import testutils

from invenio_access import InvenioAccess
from invenio_access.loaders import load_permissions_on_identity_loaded
from invenio_access.permissions import any_user, authenticated_user


def test_load_permissions_on_request_loaded(app):
    """Checks that the needs are loaded during request in the user Identity."""
    InvenioAccess(app)
    with app.test_request_context():
        with app.test_client() as client:
            client.get('/')
            assert g.identity.provides == {any_user}


def test_load_permissions_on_identity_loaded(app):
    """Check that the needs are loaded properly in the user Identity."""
    InvenioAccess(app)

    with app.test_request_context():
        identity_changed.send(current_app._get_current_object(),
                              identity=AnonymousIdentity())
        assert g.identity.provides == {any_user}

    with app.test_request_context():
        user = testutils.create_test_user('test@example.org')
        login_user(user)
        assert g.identity.provides == {
            any_user, authenticated_user, UserNeed(user.id)
        }
        logout_user()
        # FIXME: The user is still authenticatd when the identity loader
        # is called during logout. We could filter on AnonymousIdentity, but
        # This would be inconsistent as the UserNeed(user.id) is still there.
        # This will pass even if it is unexpected:
        # assert g.identity.provides == {
        #     any_user, authenticated_user, UserNeed(user.id)
        # }
        # Forcing the identity to reload again cleans the mess. In practice
        # this won't be needed as the identity is reloaded between requests.
        identity_changed.send(current_app._get_current_object(),
                              identity=AnonymousIdentity())
        assert g.identity.provides == {any_user}


def test_disabled_loader(app):
    """Check that system role loading function can be disabled."""
    app.config.update(ACCESS_LOAD_SYSTEM_ROLE_NEEDS=False)
    InvenioAccess(app)

    assert load_permissions_on_identity_loaded not in \
        identity_loaded.receivers.values()

    with app.test_request_context():
        identity_changed.send(current_app._get_current_object(),
                              identity=AnonymousIdentity())
        assert g.identity.provides == set()
