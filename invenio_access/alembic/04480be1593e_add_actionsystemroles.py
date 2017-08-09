# -*- coding: utf-8 -*-
# This file is part of Invenio.
# Copyright (C) 2017 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Add ActionSystemRoles."""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '04480be1593e'
down_revision = 'dbe499bfda43'
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.create_table(
        'access_actionssystemroles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=80), nullable=True),
        sa.Column('exclude', sa.Boolean(name='exclude'), server_default='0',
                  nullable=False),
        sa.Column('argument', sa.String(length=255), nullable=True),
        sa.Column('role_name', sa.String(length=40), nullable=False),
        sa.PrimaryKeyConstraint('id',
                                name=op.f('pk_access_actionssystemroles')),
        sa.UniqueConstraint('action', 'exclude', 'argument', 'role_name',
                            name='access_actionssystemroles_unique')
    )
    op.create_index(op.f('ix_access_actionssystemroles_action'),
                    'access_actionssystemroles', ['action'], unique=False)
    op.create_index(op.f('ix_access_actionssystemroles_argument'),
                    'access_actionssystemroles', ['argument'], unique=False)
    op.create_index(op.f('ix_access_actionssystemroles_role_name'),
                    'access_actionssystemroles', ['role_name'], unique=False)


def downgrade():
    """Downgrade database."""
    op.drop_index(op.f('ix_access_actionssystemroles_role_name'),
                  table_name='access_actionssystemroles')
    op.drop_index(op.f('ix_access_actionssystemroles_argument'),
                  table_name='access_actionssystemroles')
    op.drop_index(op.f('ix_access_actionssystemroles_action'),
                  table_name='access_actionssystemroles')
    op.drop_table('access_actionssystemroles')
