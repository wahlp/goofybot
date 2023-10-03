import asyncio
import logging
import os
import ssl
import typing

import sqlalchemy as sa
from aiomysql.sa import Engine, create_engine
from sqlalchemy.dialects.mysql import insert

from .tables import Tables

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Manager:
    def __init__(self):
        self.engine: Engine = None

    async def setup(self):
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.load_verify_locations(cafile="/etc/ssl/certs/ca-certificates.crt")

        self.engine = await create_engine(
            host=os.getenv("HOST"),
            user=os.getenv("USERNAME"),
            password=os.getenv("PASSWORD"),
            db=os.getenv("DATABASE"),
            loop=asyncio.get_event_loop(),
            ssl=ctx
        )
        logger.info('database connection established')

        self.tables = Tables()

    # === reactions ===

    async def add_reaction_record(self, reaction, member_id, message_id, timestamp):
        logger.info(f'Added reaction: {reaction=}, {member_id=}, {message_id=}, {timestamp=}')

        async with self.engine.acquire() as conn:
            async with conn.begin() as transaction:
                insert_stmt = insert(self.tables.reactions).values(
                    reaction=reaction, 
                    member_id=member_id, 
                    message_id=message_id, 
                    timestamp=sa.func.now()
                )
                
                # update timestamp if the 3-col-unique combo already exists
                upsert_stmt = insert_stmt.on_duplicate_key_update(
                    timestamp=sa.func.now()
                )
                await conn.execute(upsert_stmt)
                await transaction.commit()

    async def delete_reaction_record(self, reaction, member_id, message_id):
        logger.info(f'Removed reaction: {reaction=}, {member_id=}, {message_id=}')

        async with self.engine.acquire() as conn:
            async with conn.begin() as transaction:
                stmt = (
                    self.tables.reactions.delete()
                    .where(self.tables.reactions.c.reaction == reaction)
                    .where(self.tables.reactions.c.member_id == member_id) 
                    .where(self.tables.reactions.c.message_id == message_id)
                )
                await conn.execute(stmt)
                await transaction.commit()

    async def rename_reaction_records(self, reaction_old_name, reaction_new_name):
        logger.info(f'Updating reaction name: {reaction_old_name=}, {reaction_new_name=}')

        async with self.engine.acquire() as conn:
            async with conn.begin() as transaction:
                stmt = (
                    self.tables.reactions.update()
                    .where(self.tables.reactions.c.reaction==reaction_old_name)
                    .values(reaction=reaction_new_name)
                )
                await conn.execute(stmt)
                await transaction.commit()

    async def dump(self):
        async with self.engine.acquire() as conn:
            stmt = sa.select([
                self.tables.reactions.c.reaction,
                self.tables.reactions.c.member_id,
                self.tables.reactions.c.message_id,
                sa.func.convert_tz(self.tables.reactions.c.timestamp, '+00:00', '+08:00').label('timestamp')
            ]).order_by(self.tables.reactions.c.timestamp.desc())
            res = await conn.execute(stmt)
            
            rows = []
            async for row in res:
                rows.append(f'{row.reaction}, {row.member_id}, {row.message_id}, {row.timestamp}')
        
        return '\n'.join(rows)

    async def get_stats(self, member_id: int = None, limit: int = None):
        params = {}

        if member_id is not None:
            where_clause = 'WHERE member_id = :member_id'
            params['member_id'] = member_id
        else:
            where_clause = ''

        if limit is not None:
            limit_clause = 'LIMIT :limit'
            params['limit'] = limit
        else:
            limit_clause = ''

        async with self.engine.acquire() as conn:
            stmt = sa.text(f'''
                SELECT reaction, COUNT(*) AS count
                FROM {self.tables.reactions.name}
                {where_clause}
                GROUP BY reaction
                ORDER BY count DESC
                {limit_clause};
            ''')
            res = await conn.execute(stmt.bindparams(**params))

            stats = await res.fetchall()
            # fetchall gives a list of aiomysql.sa.ResultProxy
            # which turn into strings of key names when unpacked like tuples
            # who designed this??? 
            # i just want to talk
            return [x.as_tuple() for x in stats]
        

    # === phrases ===

    async def get_tracked_phrases(self):
        async with self.engine.acquire() as conn:
            stmt = sa.select([
                self.tables.phrases.c.phrase,
                self.tables.phrases.c.vanity_name,
            ])
            res = await conn.execute(stmt)
            rows = await res.fetchall()
            
            return [x.as_tuple() for x in rows]

    async def upsert_tracked_phrase(self, phrase: str, vanity_name: str):
        logger.info(f'updating phrase: {phrase=}, {vanity_name=}')
        async with self.engine.acquire() as conn:
            async with conn.begin() as transaction:
                insert_stmt = insert(self.tables.phrases).values(
                    phrase=phrase,
                    vanity_name=vanity_name,
                )
                
                upsert_stmt = insert_stmt.on_duplicate_key_update(
                    vanity_name=vanity_name
                )
                result = await conn.execute(upsert_stmt)
                await transaction.commit()

        return result.rowcount

    async def delete_tracked_phrase(self, phrase: str):
        logger.info(f'deleting phrase: {phrase=}')
        async with self.engine.acquire() as conn:
            async with conn.begin() as transaction:
                stmt = (
                    self.tables.phrases.delete()
                    .where(self.tables.phrases.c.phrase == phrase)
                )
                
                result = await conn.execute(stmt)
                await transaction.commit()

        return result.rowcount        

    # === phrase_usage ===

    async def update_tracked_phrase_count(self, member_id: int, phrase: str, num: int):
        logger.info(f'updating phrase count: {member_id=} {phrase=}, {num=}')
        async with self.engine.acquire() as conn:
            async with conn.begin() as transaction:
                insert_stmt = insert(self.tables.phrase_usage).values(
                    member_id=member_id,
                    phrase=phrase,
                    count=num
                )
                
                # update timestamp if the 3-col-unique combo already exists
                upsert_stmt = insert_stmt.on_duplicate_key_update(
                    count=self.tables.phrase_usage.c.count + num
                )
                await conn.execute(upsert_stmt)
                await transaction.commit()

    async def get_tracked_phrase_count(self, member_id: int, phrase: str):
        async with self.engine.acquire() as conn:
            subquery = sa.select([
                self.tables.phrase_usage.c.phrase,
                self.tables.phrase_usage.c.member_id,
                self.tables.phrase_usage.c.count
            ]).where(
                self.tables.phrase_usage.c.member_id == member_id
            ).alias()
            
            stmt = (
                sa.select([                   
                    self.tables.phrases.c.vanity_name,
                    sa.func.coalesce(subquery.c.count, sa.literal(0)).label('count')
                ]).select_from(
                    self.tables.phrases.outerjoin(
                        subquery, self.tables.phrases.c.phrase == subquery.c.phrase
                    )
                ).where(
                    self.tables.phrases.c.phrase == phrase
                )
            )
            res = await conn.execute(stmt)
            rows = await res.fetchall()
            return [x.as_tuple() for x in rows]

    # === counters ===

    async def create_counter(self, name: str, message: str):
        # actually is also able to change the message on existing self.tables.counters
        # but im not sure how to rename/split the bot command if this function's name was changed
        async with self.engine.acquire() as conn:
            async with conn.begin() as transaction:
                insert_stmt = insert(self.tables.counters).values(
                    name=name,
                    message=message
                )
                upsert_stmt = insert_stmt.on_duplicate_key_update(
                    message=message
                )
                result = await conn.execute(upsert_stmt)
                await transaction.commit()

        return result.rowcount

    async def show_counter_value(self, name: str):
        async with self.engine.acquire() as conn:
            j = sa.join(
                self.tables.counters, 
                self.tables.counter_incidents, 
                self.tables.counters.c.name == self.tables.counter_incidents.c.name,
                isouter=True
            )
            stmt = (
                sa.select([
                    sa.func.count(self.tables.counter_incidents.c.name),
                    self.tables.counters.c.message
                ])
                .select_from(j)
                .where(self.tables.counters.c.name == name)
            )
            res = await conn.execute(stmt)
            
            rows = await res.fetchall()
            return [x.as_tuple() for x in rows]
    
    async def show_counter_leaderboards(self, name: str, limit: int = 10):
        async with self.engine.acquire() as conn:
            j = sa.join(
                self.tables.counters, 
                self.tables.counter_incidents, 
                self.tables.counters.c.name == self.tables.counter_incidents.c.name
            )
            stmt = (
                sa.select([
                    sa.func.coalesce(self.tables.counter_incidents.c.instigator, self.tables.counter_incidents.c.reporter).label('contributor'),
                    sa.func.count(),
                    self.tables.counters.c.message
                ])
                .select_from(j)
                .where(self.tables.counter_incidents.c.name == name)
                .group_by('contributor')
                .order_by(sa.func.count().desc())
                .limit(limit)
            )
            res = await conn.execute(stmt)
            rows = await res.fetchall()
            
            return [x.as_tuple() for x in rows]

    async def record_counter_incident(
        self, 
        counter_name: str, 
        reporter_id: int,
        instigator_id: typing.Union[int, None], 
    ):
        async with self.engine.acquire() as conn:
            async with conn.begin() as transaction:
                stmt = insert(self.tables.counter_incidents).values(
                    name=counter_name,
                    instigator=instigator_id,
                    timestamp=sa.func.now(),
                    reporter=reporter_id
                )

                result = await conn.execute(stmt)
                await transaction.commit()

        return result.rowcount
        
    async def get_counter_names(self):
        async with self.engine.acquire() as conn:
            stmt = (
                sa.select([
                    self.tables.counters.c.name
                ])
            )
            res = await conn.execute(stmt)
            rows = await res.fetchall()
            
            return [x[0] for x in rows]

    async def ping(self):
        async with self.engine.acquire() as conn:
            await conn.execute('select 1')