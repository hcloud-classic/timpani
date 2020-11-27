"""init

Revision ID: 0fde681148ea
Revises: 
Create Date: 2020-11-19 08:25:39.076044

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0fde681148ea'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'node_info',
        sa.Column('name', sa.String(50)),
        sa.Column('ip', sa.String(50)),
        sa.Column('description', sa.String(50)),
    )


def downgrade():
    op.drop_table('node_info')
