#
# This file is part of Invenio.
# Copyright (C) 2016, 2017 CERN.
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

"""Create access tables."""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '2f63be7b7572'
down_revision = '67ba0de65fbb'
branch_labels = ()
depends_on = '9848d0149abd'


def upgrade():
    """Upgrade database."""
    op.create_table(
        'access_actionsroles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=80), nullable=True),
        sa.Column('exclude', sa.Boolean(name='exclude'), server_default='0',
                  nullable=False),
        sa.Column('argument', sa.String(length=255), nullable=True),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], [u'accounts_role.id'],
                                name='fk_access_actionroles_role_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('action', 'exclude', 'argument', 'role_id',
                            name='access_actionsroles_unique')
    )
    op.create_index(
        op.f('ix_access_actionsroles_action'), 'access_actionsroles',
        ['action'], unique=False)
    op.create_index(
        op.f('ix_access_actionsroles_argument'), 'access_actionsroles',
        ['argument'], unique=False)
    op.create_table(
        'access_actionsusers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=80), nullable=True),
        sa.Column('exclude', sa.Boolean(name='exclude'), server_default='0',
                  nullable=False),
        sa.Column('argument', sa.String(length=255), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], [u'accounts_user.id'],
                                name='fk_access_actionusers_user_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('action', 'exclude', 'argument', 'user_id',
                            name='access_actionsusers_unique')
    )
    op.create_index(
        op.f('ix_access_actionsusers_action'), 'access_actionsusers',
        ['action'], unique=False)
    op.create_index(
        op.f('ix_access_actionsusers_argument'), 'access_actionsusers',
        ['argument'], unique=False)


def downgrade():
    """Downgrade database."""
    op.drop_index(
        op.f('ix_access_actionsusers_argument'),
        table_name='access_actionsusers'
    )
    op.drop_index(
        op.f('ix_access_actionsusers_action'),
        table_name='access_actionsusers'
    )
    op.drop_table('access_actionsusers')
    op.drop_index(
        op.f('ix_access_actionsroles_argument'),
        table_name='access_actionsroles'
    )
    op.drop_index(
        op.f('ix_access_actionsroles_action'),
        table_name='access_actionsroles'
    )
    op.drop_table('access_actionsroles')
