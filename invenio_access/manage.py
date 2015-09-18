# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Perform access operations."""

from __future__ import print_function

import sys

from invenio.ext.script import Manager

from invenio.ext.sqlalchemy import db

from invenio_accounts.models import User

from sqlalchemy.exc import IntegrityError

from sqlalchemy.orm.exc import NoResultFound

from .models import AccROLE, UserAccROLE

manager = Manager(usage=__doc__)

MSG_FAILED_TO_ADD_ROLE = 'failed to add a role:'
MSG_FAILED_TO_REMOVE_ROLE = 'failed to remove a role:'
MSG_FAILED_TO_GET_ROLES_FOR_USER = 'failed to get roles for user:'


@manager.command
@manager.option('email', dest='email')
@manager.option('role_name', dest='role_name')
@manager.option('--verbose', '-v', dest='verbose', action='store_true')
def add(email, role_name, verbose=False):
    """Add a role for a user."""
    user_role = UserAccROLE()
    user_role.id_user = User.query.filter_by(
        email=email).with_entities(User.id).scalar()
    user_role.id_accROLE = AccROLE.query.filter_by(
        name=role_name).with_entities(AccROLE.id).scalar()

    if user_role.id_user is None:
        print("user {0} doesn't exist".format(email), file=sys.stderr)
        exit(1)
    if user_role.id_accROLE is None:
        print("role {0} doesn't exist".format(role_name), file=sys.stderr)
        exit(1)

    try:
        with db.session.begin_nested():
            db.session.add(user_role)
        db.session.commit()
        if verbose:
            print('successfully added role {0} for user {1}'.format(
                role_name, email))
    except IntegrityError:
        if verbose:
            print(
                '{0} was already assigned {1} role'.format(email, role_name))


@manager.command
@manager.option('email', dest='email')
@manager.option('role_name', dest='role_name')
@manager.option('--verbose', '-v', dest='verbose', action='store_true')
def remove(email, role_name, verbose=False):
    """Remove a role from a user.

    Succeeds even if the user didn't have the role.
    """
    try:
        with db.session.begin_nested():
            user_role = UserAccROLE.query.join(AccROLE, User).filter(
                User.email == email, AccROLE.name == role_name).one()
            db.session.delete(user_role)
        db.session.commit()
        if verbose:
            print('removed role {0} from user {1}'.format(role_name, email))
    except NoResultFound:
        if verbose:
            print("user {0} didn't have the role {1}".format(email, role_name))


@manager.command
@manager.option('--email', '-e', dest='email')
@manager.option('--verbose', '-v', dest='verbose', action='store_true')
def roles(email=None, verbose=False):
    """Print available roles.

    Specify --email <email> to list roles of a given user.
    """
    query = AccROLE.query

    if email is not None:
        query = query.join(UserAccROLE, User).filter(User.email == email)

    roles = query.all()

    if len(roles) == 0 and verbose:
        if email is None:
            print('no roles available in database')
        else:
            print('no roles found for user {0}'.format(email))
    elif len(roles) > 0:
        longest = max([len(role.name) for role in roles])
        for role in roles:
            if verbose:
                print(role.name.ljust(longest), '-', role.description)
            else:
                print(role.name)


def main():
    """Run manager."""
    from invenio.base.factory import create_app
    app = create_app()
    manager.app = app
    manager.run()
