# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Prevent NULL in ActionUsers for stability reasons."""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "dbe499bfda43"
down_revision = "2069a982633b"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.drop_constraint(
        "fk_access_actionsusers_user_id_accounts_user",
        "access_actionsusers",
        type_="foreignkey",
    )
    op.drop_index(
        op.f("ix_access_actionsusers_user_id"), table_name="access_actionsusers"
    )

    op.alter_column(
        "access_actionsusers", "user_id", nullable=False, existing_type=sa.Integer()
    )

    op.create_index(
        op.f("ix_access_actionsusers_user_id"),
        "access_actionsusers",
        ["user_id"],
        unique=False,
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
        "fk_access_actionsusers_user_id_accounts_user",
        "access_actionsusers",
        type_="foreignkey",
    )
    op.drop_index(
        op.f("ix_access_actionsusers_user_id"), table_name="access_actionsusers"
    )

    op.alter_column(
        "access_actionsusers", "user_id", nullable=True, existing_type=sa.Integer()
    )

    op.create_index(
        op.f("ix_access_actionsusers_user_id"),
        "access_actionsusers",
        ["user_id"],
        unique=False,
    )
    op.create_foreign_key(
        op.f("fk_access_actionsusers_user_id_accounts_user"),
        "access_actionsusers",
        "accounts_user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
