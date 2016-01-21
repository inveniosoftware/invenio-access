# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
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

"""Admin views for managing access to actions."""

from flask import current_app, flash
from flask_admin.actions import action
from flask_admin.contrib.sqla import ModelView
from flask_admin.form.fields import DateTimeField
from flask_login import login_user, logout_user
from werkzeug.local import LocalProxy
from wtforms import SelectField

from .models import ActionRoles, ActionUsers
from .proxies import current_access

_datastore = LocalProxy(lambda: current_app.extensions['security'].datastore)


def _(x):
    """Identity."""
    return x


class ActionUsersView(ModelView):
    """View for managing access to actions by users."""

    can_view_details = True

    list_all = ('user_id', 'user.email', 'action', 'exclude', 'argument')

    column_list = list_all
    column_default_sort = ('user_id', True)

    column_labels = {
        'user.email': _("Email"),
        'user_id': _("User ID"),
    }

    column_filters = list_all

    form_args = dict(
        action=dict(
            choices=LocalProxy(lambda: [
                (action, action) for action in current_access.actions.keys()
            ])
        )
    )
    form_overrides = dict(
        action=SelectField,
    )


class ActionRolesView(ModelView):
    """View for managing access to actions by users with given role."""

    can_view_details = True

    list_all = ('role.name', 'action', 'exclude', 'argument')

    column_list = list_all

    column_filters = \
        columns_sortable_list = \
        columns_searchable_list = \
        list_all

    column_display_all_relations = True

    column_labels = {
        'role.name': _("Role Name"),
    }


action_roles_adminview = {
    'model': ActionRoles,
    'modelview': ActionRolesView,
    'category': _('User Management'),
}

action_users_adminview = {
    'model': ActionUsers,
    'modelview': ActionUsersView,
    'category': _('User Management'),
}

__all__ = ('action_users_adminview', 'action_roles_adminview', )
