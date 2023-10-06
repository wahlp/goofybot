import logging
import os

import discord
from discord.ext import commands

from lib import db

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

logger = logging.getLogger(__name__)

class CustomBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='?', intents=intents)
        self.db_manager = None

        self.tracked_phrases = None
        self.counter_names = None

    async def setup(self):
        self.db_manager = db.Manager()
        await self.db_manager.setup()

        # setup autocomplete values
        await self.fetch_phrases()
        await self.fetch_counters()
        
        for cog_name in get_cogs():
            await self.load_extension(cog_name)
        logger.info('loaded all cogs')

    async def fetch_phrases(self):
        self.tracked_phrases = await self.db_manager.get_tracked_phrases()

    async def fetch_counters(self):
        self.counter_names = await self.db_manager.get_counter_names()

    async def reload_cogs(self):
        for cog_name in get_cogs():
            await self.reload_extension(cog_name)
        logger.info('reloaded all cogs')
        
    async def format_leaderboards(
        self, 
        data: list[int, int], 
        name: str, 
        purpose: str,
        missing_id_string: str = '',
    ):
        lines = []
        for user_id, count in data:
            if user_id is None:
                line = missing_id_string.format(count=count)
            else:
                user = self.get_user(user_id)
                if user is None:
                    user = await self.bot.fetch_user(user_id)
                line = f'{user.mention}: {count}'
            lines.append(line)

        msg = '\n'.join(lines)
        embed = discord.Embed(
            title=f'Leaderboards for {purpose} - {name}',
            description=msg
        )
        return embed


def get_cogs():
    cog_file_names = []
    for x in os.listdir('cogs'):
         if x[-3:] == '.py':
            full_cog_name = f'cogs.{x[:-3]}'
            cog_file_names.append(full_cog_name)

    return cog_file_names