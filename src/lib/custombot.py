import logging
import os

import discord
from discord.ext import commands

from lib import db


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class CustomBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='?', intents=intents)
        self.db_manager = None
        self.tracked_phrases = None

    async def setup(self):
        self.db_manager = db.Manager()
        await self.db_manager.setup()
        await self.fetch_phrases()
        
        for cog_name in get_cogs():
            await self.load_extension(cog_name)
        logger.info('loaded all cogs')

    async def fetch_phrases(self):
        self.tracked_phrases = await self.db_manager.get_tracked_phrases()

    async def reload_cogs(self):
        for cog_name in get_cogs():
            await self.reload_extension(cog_name)
        logger.info('reloaded all cogs')


def get_cogs():
    cog_file_names = []
    for x in os.listdir('cogs'):
         if x[-3:] == '.py':
            full_cog_name = f'cogs.{x[:-3]}'
            cog_file_names.append(full_cog_name)

    return cog_file_names