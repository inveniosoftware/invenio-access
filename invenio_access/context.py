# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2025 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Introduce context_identity."""

from contextvars import ContextVar

from .permissions import system_identity

context_identity = ContextVar("identity")


def set_system_identity():
    """Set system identity."""
    context_identity.set(system_identity)


def set_identity(sender, identity):
    """Set identity."""
    context_identity.set(identity)
