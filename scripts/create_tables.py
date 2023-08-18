import asyncio
import os
import ssl

import sqlalchemy as sa
from aiomysql.sa import create_engine

from src.lib.tables import reactions, phrases, phrase_usage

async def main():
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.load_verify_locations(cafile="/etc/ssl/certs/ca-certificates.crt")

    engine = await create_engine(
        host=os.getenv("HOST"),
        user=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
        db=os.getenv("DATABASE"),
        loop=asyncio.get_event_loop(),
        ssl=ctx,
    )

    async with engine.acquire() as conn:
        for table in [reactions, phrases, phrase_usage]:
            try:
                stmt = sa.schema.CreateTable(table)
                await conn.execute(stmt)
                print(f'created table {table.name}')
            except Exception as e:
                print(e)
                print(f'did not create table {table.name}')

    

if __name__ == '__main__':
    asyncio.run(main())