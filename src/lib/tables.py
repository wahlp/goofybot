import os

import sqlalchemy as sa


metadata = sa.MetaData()

reactions = sa.Table(
    os.getenv('TABLE_REACTIONS'),
    metadata,
    sa.Column('reaction', sa.String(40), nullable=False, primary_key=True),
    sa.Column('member_id', sa.BigInteger, nullable=False, primary_key=True),
    sa.Column('message_id', sa.BigInteger, nullable=False, primary_key=True),
    sa.Column('timestamp', sa.TIMESTAMP, nullable=False),
)

phrases = sa.Table(
    os.getenv('TABLE_PHRASES'),
    metadata,
    sa.Column('phrase', sa.String(128), nullable=False, primary_key=True),
    sa.Column('vanity_name', sa.String(40), nullable=False)
)

phrase_usage = sa.Table(
    os.getenv('TABLE_PHRASE_USAGE'),
    metadata,
    sa.Column('member_id', sa.BigInteger, nullable=False, primary_key=True),
    sa.Column('phrase', sa.String(128), nullable=False, primary_key=True,),
    sa.Column('count', sa.Integer, default=0, nullable=False),
)

counters = sa.Table(
    os.getenv('TABLE_COUNTERS'),
    metadata,
    sa.Column('name', sa.String(32), nullable=False, primary_key=True),
    sa.Column('message', sa.String(256), nullable=False)
)

counter_incidents = sa.Table(
    os.getenv('TABLE_COUNTER_INCIDENTS'),
    metadata,
    sa.Column('name', sa.String(32), nullable=False),
    sa.Column('instigator', sa.BigInteger, nullable=True),
    sa.Column('timestamp', sa.TIMESTAMP, nullable=False),
)