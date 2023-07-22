import asyncio
import os
import ssl

import sqlalchemy as sa
from aiomysql.sa import create_engine
# from sqlalchemy import Table, DDL

# from src.lib.tables import metadata
from src.lib.tables import reactions, phrases, phrase_usage

# def create_table_ddl(table: Table):
#     ddl = DDL(f"CREATE TABLE IF NOT EXISTS {table.name} ({table})")
#     return ddl

# ddl = create_table_ddl(reactions)

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
        # ddl=ddl,
    )

    async with engine.acquire() as conn:
        # metadata.create_all(conn)
        for table in [reactions, phrases, phrase_usage]:
            # if not sa.inspect(engine).has_table(table.name):
            try:
                stmt = sa.schema.CreateTable(table)
                await conn.execute(stmt)
                print(f'created table {table.name}')
            except Exception as e:
                print(e)
                print(f'did not create table {table.name}')

    

if __name__ == '__main__':
    # print(ddl)
    asyncio.run(main())