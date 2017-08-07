# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.
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
