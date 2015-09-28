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

"""Provide API-callable functions for access management."""

from intbitset import intbitset

from invenio_accounts.models import User, Usergroup, UserUsergroup

from invenio_base.globals import cfg

from invenio_ext import principal
from invenio_ext.sqlalchemy import db

from six import iteritems

from . import models
from .local_config import DEF_AUTHS, DEF_ROLES, DEF_USERS, SUPERADMINROLE


def get_action_roles(id_action):
    """Return all the roles connected with an action."""
    id_superadmin_role = models.AccROLE.factory(name=SUPERADMINROLE).id
    return models.AccAuthorization.query.filter(db.or_(
        models.AccAuthorization.id_accACTION == id_action,
        models.AccAuthorization.id_accROLE == id_superadmin_role
    )).distinct().all()


def get_roles_emails(id_roles):
    """Get emails by roles."""
    return set(
        map(lambda u: u.email.lower().strip(),
            db.session.query(db.func.distinct(User.email)).join(
                User.active_roles
            ).filter(
                models.UserAccROLE.id_accROLE.in_(id_roles)).all()))


def find_possible_roles(name_action, always_add_superadmin=True,
                        batch_args=False, **arguments):
    """Find all the possible roles that are enabled to a given action.

    :return: roles as a list of role_id
    """
    query_roles_without_args = \
        db.select([models.AccAuthorization.id_accROLE], db.and_(
            models.AccAuthorization.argumentlistid <= 0,
            models.AccAuthorization.id_accACTION == db.bindparam('id_action')))

    query_roles_with_args = \
        models.AccAuthorization.query.filter(db.and_(
            models.AccAuthorization.argumentlistid > 0,
            models.AccAuthorization.id_accACTION == db.bindparam('id_action')
        )).join(models.AccAuthorization.argument)

    id_action = db.session.query(models.AccACTION.id).filter(
        models.AccACTION.name == name_action).scalar()
    roles = intbitset(db.engine.execute(query_roles_without_args.params(
        id_action=id_action)).fetchall())

    if always_add_superadmin:
        roles.add(cfg["CFG_SUPERADMINROLE_ID"] or 1)

    # Unpack arguments
    if batch_args:
        batch_arguments = [dict(zip(arguments.keys(), values))
                           for values in zip(*arguments.values())]
    else:
        batch_arguments = [arguments]

    acc_authorizations = query_roles_with_args.params(
        id_action=id_action
    ).all()

    result = []
    for arguments in batch_arguments:
        batch_roles = roles.copy()
        for auth in acc_authorizations:
            if auth.id_accROLE not in batch_roles:
                if not ((auth.argument.value != arguments.get(
                    auth.argument.keyword, '*') != '*'
                ) and auth.argument.value != '*'):
                    batch_roles.add(auth.id_accROLE)
        result.append(batch_roles)
    return result if batch_args else result[0]


def reset_default_settings(superusers=(),
                           additional_def_user_roles=(),
                           additional_def_roles=(),
                           additional_def_auths=()):
    """reset to default by deleting everything and adding default.

    superusers - list of superuser emails

    additional_def_user_roles - additional list of pair email, rolename
    (see DEF_DEMO_USER_ROLES in access_control_config.py)

    additional_def_roles - additional list of default list of roles
    (see DEF_DEMO_ROLES in access_control_config.py)

    additional_def_auths - additional list of default authorizations
    (see DEF_DEMO_AUTHS in access_control_config.py)
    """
    remove = delete_all_settings()
    add = add_default_settings(
        superusers, additional_def_user_roles,
        additional_def_roles, additional_def_auths)

    return remove, add


def add_default_users(users, usergroups, userusergroups):
    """Add default useris, usergroups and userusergroups."""
    # add users
    for user_tuple in users:
        if User.exists(User.email == user_tuple[1]):
            # update
            user = User.query.filter_by(email=user_tuple[1]).first()
            user.nickname = user_tuple[0]
            user.password = user_tuple[2]
            user.note = user_tuple[3]
            db.session.merge(user)
        else:
            # insert
            user = User(nickname=user_tuple[0],
                        email=user_tuple[1],
                        password=user_tuple[2],
                        note=user_tuple[3])
            db.session.add(user)
        db.session.commit()
    # add usergroups
    for usergroup_tuple in usergroups:
        if Usergroup.exists(Usergroup.name == usergroup_tuple[0]):
            # update
            usergroup = Usergroup.query.filter_by(
                name=usergroup_tuple[0]).first()
            usergroup.description = usergroup_tuple[1]
            db.session.merge(usergroup)
        else:
            # insert
            usergroup = Usergroup(name=usergroup_tuple[0],
                                  description=usergroup_tuple[1])
            db.session.add(usergroup)
        db.session.commit()
    # add userusergroups
    for userusergroup_tuple in userusergroups:
        user = User.query.filter_by(nickname=userusergroup_tuple[0]).first()
        usergroup = Usergroup.query.filter_by(
            name=userusergroup_tuple[1]).first()
        uug_filters = [
            UserUsergroup.id_user == user.id,
            UserUsergroup.id_usergroup == usergroup.id,
        ]
        if UserUsergroup.exists(*uug_filters):
            # update
            userusergroup = UserUsergroup.query.filter(*uug_filters).first()
            userusergroup.user_status = userusergroup_tuple[2]
            db.session.merge(userusergroup)
        else:
            # insert
            userusergroup = UserUsergroup(id_user=user.id,
                                          id_usergroup=usergroup.id,
                                          user_status=userusergroup_tuple[2])
            db.session.add(userusergroup)
        db.session.commit()


def add_default_settings(superusers=(),
                         additional_def_user_roles=(),
                         additional_def_roles=(),
                         additional_def_auths=()):
    """Add the default settings if they don't exist.

    :param superusers: list of superuser emails
    :param additional_def_user_roles: additional list of pair email, rolename
        (see DEF_DEMO_USER_ROLES in access_control_config.py)
    :param additional_def_roles: additional list of default list of roles
        (see DEF_DEMO_ROLES in access_control_config.py)
    :param additional_def_auths: additional list of default authorizations
        (see DEF_DEMO_AUTHS in access_control_config.py)
    """
    # add new superusers
    for user in superusers:
        DEF_USERS.append(user)

    # ensure admin is in default users
    if cfg['CFG_SITE_ADMIN_EMAIL'] not in DEF_USERS:
        DEF_USERS.append(cfg['CFG_SITE_ADMIN_EMAIL'])

    # add roles

    insroles = []
    # define dictiory with default roles
    def_roles = dict([(role[0], role[1:]) for role in DEF_ROLES])
    def_roles.update(
        dict([(role[0], role[1:]) for role in additional_def_roles]))
    # insert new roles
    for name, (description, firerole_def_src) in iteritems(def_roles):
        # try to add, don't care if description is different
        role = models.AccROLE.factory(
            name=name,
            description=description,
            firerole_def_src=firerole_def_src
        )
        insroles.append(role)

    # add users as superadmin (role)
    users = User.query.filter(User.email.in_(DEF_USERS)).all()
    superadmin_role = models.AccROLE.query.filter_by(name=SUPERADMINROLE).one()
    insuserroles = []
    for user in users:
        useraccrole = models.UserAccROLE.factory(
            id_user=user.id,
            id_accROLE=superadmin_role.id
        )
        insuserroles.append(useraccrole)

    # add additional roles to the users
    for user_email, role_name in additional_def_user_roles:
        user = User.query.filter(User.email == user_email).one()
        role = models.AccROLE.query.filter(
            models.AccROLE.name == role_name).one()
        useraccrole = models.UserAccROLE.factory(
            id_user=user.id,
            id_accROLE=role.id
        )
        insuserroles.append(useraccrole)

    # add actions
    insactions = []
    for principal_action in principal.actions:
        action = models.AccACTION.factory(
            name=principal_action.name,
            description=principal_action.description,
            optional=principal_action.optional,
            allowedkeywords=principal_action.allowedkeywords
        )
        insactions.append(action)

    # add authorizations
    insauths = []
    def_auths = list(DEF_AUTHS) + list(additional_def_auths)
    for (name_role, name_action, args) in def_auths:
        action = models.AccACTION.query.filter_by(name=name_action).one()
        role = models.AccROLE.query.filter_by(name=name_role).one()

        # add arguments
        arguments = []
        for (key, value) in args.iteritems():
            arguments.append(models.AccARGUMENT.factory(
                keyword=key,
                value=value
            ))
        # add the authorization
        auth = models.AccAuthorization.factory(
            role=role,
            action=action,
            arguments=arguments
        )
        insauths.append(auth)

    return insroles, insactions, insuserroles, insauths


def delete_all_settings():
    """Remove all data affiliated with webaccess.

    simply remove all data affiliated with webaccess by truncating
    tables accROLE, accACTION, accARGUMENT and those connected.
    """
    from invenio_ext.sqlalchemy import db
    db.session.commit()

    models.AccROLE.delete()
    models.AccACTION.delete()
    models.AccARGUMENT.delete()
    models.UserAccROLE.delete()
    models.AccAuthorization.delete()
