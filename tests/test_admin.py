# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test for admin view."""

from invenio_access.admin import (
    action_roles_adminview,
    action_system_roles_adminview,
    action_users_adminview,
)


def test_admin(app):
    """Test flask-admin interace."""
    assert isinstance(action_roles_adminview, dict)
    assert isinstance(action_users_adminview, dict)
    assert isinstance(action_system_roles_adminview, dict)

    assert "model" in action_roles_adminview
    assert "modelview" in action_roles_adminview
    assert "model" in action_users_adminview
    assert "modelview" in action_users_adminview
    assert "model" in action_system_roles_adminview
    assert "modelview" in action_system_roles_adminview
