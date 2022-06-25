# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Add on delete cascade constraint."""

from alembic import op

# revision identifiers, used by Alembic.
revision = "2069a982633b"
down_revision = "2f63be7b7572"
branch_labels = ()
depends_on = "35c1075e6360"  # invenio-db "Force naming convention"


def upgrade():
    """Upgrade database."""
    op.create_index(
        op.f("ix_access_actionsroles_role_id"),
        "access_actionsroles",
        ["role_id"],
        unique=False,
    )
    op.drop_constraint(
        "fk_access_actionsroles_role_id_accounts_role",
        "access_actionsroles",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("fk_access_actionsroles_role_id_accounts_role"),
        "access_actionsroles",
        "accounts_role",
        ["role_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        op.f("ix_access_actionsusers_user_id"),
        "access_actionsusers",
        ["user_id"],
        unique=False,
    )
    op.drop_constraint(
        "fk_access_actionsusers_user_id_accounts_user",
        "access_actionsusers",
        type_="foreignkey",
    )
    op.create_foreign_key(
        op.f("fk_access_actionsusers_user_id_accounts_user"),
        "access_actionsusers",
        "accounts_user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade():
    """Downgrade database."""
    op.drop_constraint(
        op.f("fk_access_actionsusers_user_id_accounts_user"),
        "access_actionsusers",
        type_="foreignkey",
    )
    op.drop_index(
        op.f("ix_access_actionsusers_user_id"), table_name="access_actionsusers"
    )
    op.create_foreign_key(
        "fk_access_actionsusers_user_id_accounts_user",
        "access_actionsusers",
        "accounts_user",
        ["user_id"],
        ["id"],
    )
    op.drop_constraint(
        op.f("fk_access_actionsroles_role_id_accounts_role"),
        "access_actionsroles",
        type_="foreignkey",
    )
    op.drop_index(
        op.f("ix_access_actionsroles_role_id"), table_name="access_actionsroles"
    )
    op.create_foreign_key(
        "fk_access_actionsroles_role_id_accounts_role",
        "access_actionsroles",
        "accounts_role",
        ["role_id"],
        ["id"],
    )
