# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Admin views for managing access to actions."""

from flask import current_app
from flask_admin.contrib.sqla import ModelView
from werkzeug.local import LocalProxy
from wtforms import SelectField

from .models import ActionRoles, ActionSystemRoles, ActionUsers
from .proxies import current_access

_datastore = LocalProxy(lambda: current_app.extensions['security'].datastore)


def _(x):
    """Identity."""
    return x


class ActionUsersView(ModelView):
    """View for managing access to actions by users."""

    can_view_details = True

    list_all = ('user_id', 'user.email', 'action', 'argument', 'exclude')

    column_list = list_all

    column_default_sort = ('user_id', True)

    column_labels = {
        'user.email': _("Email"),
        'user_id': _("User ID"),
        'exclude': _("Deny"),
    }

    column_filters = list_all

    form_columns = ('user', 'action', 'argument', 'exclude')

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

    list_all = ('role.name', 'action', 'argument', 'exclude')

    column_list = list_all

    column_filters = \
        columns_sortable_list = \
        columns_searchable_list = \
        list_all

    column_display_all_relations = True

    column_labels = {
        'role.name': _("Role Name"),
        'exclude': _("Deny"),
    }

    form_columns = ('role', 'action', 'argument', 'exclude')

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


class ActionSystemRolesView(ModelView):
    """View for managing access to actions by users with system roles."""

    can_view_details = True

    list_all = ('role_name', 'action', 'argument', 'exclude')

    column_list = list_all

    column_filters = \
        columns_sortable_list = \
        columns_searchable_list = \
        list_all

    column_display_all_relations = True

    column_labels = {
        'role_name': _("System Role"),
        'exclude': _("Deny"),
    }

    form_args = dict(
        action=dict(
            choices=LocalProxy(lambda: [
                (action, action) for action in current_access.actions.keys()
            ])
        ),
        role_name=dict(
            choices=LocalProxy(lambda: [
                (action, action) for action
                in current_access.system_roles.keys()
            ])
        )
    )

    form_columns = ('role_name', 'action', 'argument', 'exclude')
    form_overrides = dict(
        action=SelectField,
        role_name=SelectField,
    )


action_roles_adminview = {
    'model': ActionRoles,
    'modelview': ActionRolesView,
    'category': _('User Management'),
    'name': _('Access: Roles')
}

action_users_adminview = {
    'model': ActionUsers,
    'modelview': ActionUsersView,
    'category': _('User Management'),
    'name': _('Access: Users')
}

action_system_roles_adminview = {
    'model': ActionSystemRoles,
    'modelview': ActionSystemRolesView,
    'category': _('User Management'),
    'name': _('Access: System Roles')
}

__all__ = ('action_users_adminview', 'action_roles_adminview',
           'action_system_roles_adminview')
