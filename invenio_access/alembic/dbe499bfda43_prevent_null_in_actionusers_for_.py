#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
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

"""Prevent NULL in ActionUsers for stability reasons."""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'dbe499bfda43'
down_revision = '2069a982633b'
branch_labels = ()
depends_on = None


def upgrade():
    """Upgrade database."""
    op.drop_constraint(u'fk_access_actionsusers_user_id_accounts_user',
                       'access_actionsusers', type_='foreignkey')
    op.drop_index(op.f('ix_access_actionsusers_user_id'),
                  table_name='access_actionsusers')

    op.alter_column('access_actionsusers', 'user_id', nullable=False,
                    existing_type=sa.Integer())

    op.create_index(op.f('ix_access_actionsusers_user_id'),
                    'access_actionsusers', ['user_id'], unique=False)
    op.create_foreign_key(op.f('fk_access_actionsusers_user_id_accounts_user'),
                          'access_actionsusers', 'accounts_user', ['user_id'],
                          ['id'], ondelete='CASCADE')


def downgrade():
    """Downgrade database."""
    op.drop_constraint(u'fk_access_actionsusers_user_id_accounts_user',
                       'access_actionsusers', type_='foreignkey')
    op.drop_index(op.f('ix_access_actionsusers_user_id'),
                  table_name='access_actionsusers')

    op.alter_column('access_actionsusers', 'user_id', nullable=True,
                    existing_type=sa.Integer())

    op.create_index(op.f('ix_access_actionsusers_user_id'),
                    'access_actionsusers', ['user_id'], unique=False)
    op.create_foreign_key(op.f('fk_access_actionsusers_user_id_accounts_user'),
                          'access_actionsusers', 'accounts_user', ['user_id'],
                          ['id'], ondelete='CASCADE')
