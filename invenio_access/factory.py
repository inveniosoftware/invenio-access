# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Factory method for creating new action needs."""

from functools import partial

from flask_principal import ActionNeed

from .permissions import ParameterizedActionNeed


def action_factory(name, parameter=False):
    """Factory method for creating new actions (w/wo parameters).

    :param name: Name of the action (prefix with your module name).
    :param parameter: Determines if action should take parameters or not.
        Default is ``False``.
    """
    if parameter:
        return partial(ParameterizedActionNeed, name)
    else:
        return ActionNeed(name)
