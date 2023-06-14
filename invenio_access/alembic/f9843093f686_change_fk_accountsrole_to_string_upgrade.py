#
# This file is part of Invenio.
# Copyright (C) 2023 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Change FK AccountsRole to string (upgrade recipe).

This recipe only contains the upgrade because as it directly depends on invenio-accounts recipe. That recipe is in
charge of deleting all the constraints on the role_id, including foreign keys using the role_id declared in this module.
Therefore, when in order to downgrade we need to split the recipes to be able to first execute the recipe in
invenio-accounts (f2522cdd5fcd) and after that we can execute the downgrade recipe (842a62b56e60).
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f9843093f686"
down_revision = (
    "f2522cdd5fcd",
    "842a62b56e60",
)  # Depends on invenio-accounts revision id (f2522cdd5fcd)
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.alter_column(
        "access_actionsroles",
        "role_id",
        existing_type=sa.Integer,
        type_=sa.String(80),
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


def downgrade():
    """Downgrade database."""
    pass
