import os

import sqlalchemy as sa


class Tables:
    def __init__(self):
        metadata = sa.MetaData()

        self.reactions = sa.Table(
            os.getenv('TABLE_REACTIONS'),
            metadata,
            sa.Column('reaction', sa.String(40), nullable=False, primary_key=True),
            sa.Column('member_id', sa.BigInteger, nullable=False, primary_key=True),
            sa.Column('message_id', sa.BigInteger, nullable=False, primary_key=True),
            sa.Column('timestamp', sa.TIMESTAMP, nullable=False),
        )

        self.phrases = sa.Table(
            os.getenv('TABLE_PHRASES'),
            metadata,
            sa.Column('phrase', sa.String(128), nullable=False, primary_key=True),
            sa.Column('vanity_name', sa.String(40), nullable=False)
        )

        self.phrase_usage = sa.Table(
            os.getenv('TABLE_PHRASE_USAGE'),
            metadata,
            sa.Column('member_id', sa.BigInteger, nullable=False, primary_key=True),
            sa.Column('phrase', sa.String(128), nullable=False, primary_key=True,),
            sa.Column('count', sa.Integer, default=0, nullable=False),
        )

        self.counters = sa.Table(
            os.getenv('TABLE_COUNTERS'),
            metadata,
            sa.Column('name', sa.String(32), nullable=False, primary_key=True),
            sa.Column('message', sa.String(256), nullable=False)
        )

        self.counter_incidents = sa.Table(
            os.getenv('TABLE_COUNTER_INCIDENTS'),
            metadata,
            sa.Column('name', sa.String(32), nullable=False),
            sa.Column('instigator', sa.BigInteger, nullable=True),
            sa.Column('reporter', sa.BigInteger, nullable=True),
            sa.Column('timestamp', sa.TIMESTAMP, nullable=False),
        )

    def get_all(self):
        return [
            self.counter_incidents, 
            self.counters, 
            self.phrase_usage, 
            self.phrases, 
            self.reactions
        ]