# This file is part of Invenio.
# Copyright (C) 2023 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Change FK AccountsRole to string (downgrade recipe)."""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "842a62b56e60"
down_revision = "04480be1593e"
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    pass


def downgrade():
    """Downgrade database."""
    op.alter_column(
        "access_actionsroles",
        "role_id",
        existing_type=sa.String(80),
        type_=sa.Integer,
        postgresql_using="role_id::integer",
        nullable=False,
    )
    op.create_foreign_key(
        op.f("fk_access_actionsroles_role_id_accounts_role"),
        "access_actionsroles",
        "accounts_role",
        ["role_id"],
        ["id"],
        ondelete="CASCADE",
    )
