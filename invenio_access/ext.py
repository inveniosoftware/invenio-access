# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for common role based access control."""

from __future__ import absolute_import, print_function

import pkg_resources
import six
from flask_principal import identity_loaded
from werkzeug.utils import cached_property, import_string

from . import config
from .loaders import load_permissions_on_identity_loaded


class _AccessState(object):
    """Access state storing registered actions."""

    def __init__(self, app, entry_point_actions=None,
                 entry_point_system_roles=None, cache=None):
        """Initialize state.

        :param app: The Flask application.
        :param entry_point_actions: The entrypoint for actions extensions.
            (Default: ``None``)
        :param entry_point_system_roles: The entrypoint for system roles
            extensions. (Default: ``None``)
        :param cache: The cache system. (Default: ``None``)
        """
        self.app = app
        self.actions = {}
        self.system_roles = {}
        self._cache = cache
        if entry_point_actions:
            self.load_entry_point_actions(entry_point_actions)
        if entry_point_system_roles:
            self.load_entry_point_system_roles(entry_point_system_roles)

    @cached_property
    def cache(self):
        """Return a cache instance."""
        cache = self._cache or self.app.config.get('ACCESS_CACHE')
        return import_string(cache) if isinstance(cache, six.string_types) \
            else cache

    def set_action_cache(self, action_key, data):
        """Store action needs and excludes.

        .. note:: The action is saved only if a cache system is defined.

        :param action_key: The unique action name.
        :param data: The action to be saved.
        """
        if self.cache:
            self.cache.set(
                self.app.config['ACCESS_ACTION_CACHE_PREFIX'] +
                action_key, data
            )

    def get_action_cache(self, action_key):
        """Get action needs and excludes from cache.

        .. note:: It returns the action if a cache system is defined.

        :param action_key: The unique action name.
        :returns: The action stored in cache or ``None``.
        """
        data = None
        if self.cache:
            data = self.cache.get(
                self.app.config['ACCESS_ACTION_CACHE_PREFIX'] +
                action_key
            )
        return data

    def delete_action_cache(self, action_key):
        """Delete action needs and excludes from cache.

        .. note:: It returns the action if a cache system is defined.

        :param action_key: The unique action name.
        """
        if self.cache:
            self.cache.delete(
                self.app.config['ACCESS_ACTION_CACHE_PREFIX'] +
                action_key
            )

    def register_action(self, action):
        """Register an action to be showed in the actions list.

        .. note:: A action can't be registered two times. If it happens, then
        an assert exception will be raised.

        :param action: The action to be registered.
        """
        assert action.value not in self.actions
        self.actions[action.value] = action

    def load_entry_point_actions(self, entry_point_group):
        """Load actions from an entry point group.

        :param entry_point_group: The entrypoint for extensions.
        """
        for ep in pkg_resources.iter_entry_points(group=entry_point_group):
            self.register_action(ep.load())

    def register_system_role(self, system_role):
        """Register a system role.

        .. note:: A system role can't be registered two times. If it happens,
        then an assert exception will be raised.

        :param system_role: The system role to be registered.
        """
        assert system_role.value not in self.system_roles
        self.system_roles[system_role.value] = system_role

    def load_entry_point_system_roles(self, entry_point_group):
        """Load system roles from an entry point group.

        :param entry_point_group: The entrypoint for extensions.
        """
        for ep in pkg_resources.iter_entry_points(group=entry_point_group):
            self.register_system_role(ep.load())


class InvenioAccess(object):
    """Invenio Access extension."""

    def __init__(self, app=None, **kwargs):
        """Extension initialization.

        :param app: The Flask application. (Default: ``None``)
        """
        if app:
            self._state = self.init_app(app, **kwargs)

    def init_app(self, app, entry_point_actions='invenio_access.actions',
                 entry_point_system_roles='invenio_access.system_roles',
                 **kwargs):
        """Flask application initialization.

        :param app: The Flask application.
        :param entry_point_actions: The entrypoint for actions extensions.
            (Default: ``'invenio_access.actions'``)
        :param entry_point_system_roles: The entrypoint for  system roles
            extensions. (Default: ``'invenio_access.system_roles'``)
        :param cache: The cache system. (Default: ``None``)
        """
        self.init_config(app)
        state = _AccessState(
            app, entry_point_actions=entry_point_actions,
            entry_point_system_roles=entry_point_system_roles,
            cache=kwargs.get('cache'))
        app.extensions['invenio-access'] = state

        if app.config.get('ACCESS_LOAD_SYSTEM_ROLE_NEEDS', True):
            identity_loaded.connect_via(app)(
                load_permissions_on_identity_loaded
            )

        return state

    def init_config(self, app):
        """Initialize configuration.

        :param app: The Flask application.
        """
        for k in dir(config):
            if k.startswith('ACCESS_'):
                app.config.setdefault(k, getattr(config, k))

    def __getattr__(self, name):
        """Proxy to state object."""
        return getattr(self._state, name, None)
