
import discord
from discord.ext import commands

from lib import db


intents = discord.Intents.default()
intents.message_content = True
intents.members = True


class CustomBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='?', intents=intents)
        self.db_manager = None
        self.tracked_phrases = None

    async def setup(self):
        self.db_manager = db.Manager()
        await self.db_manager.setup()
        await self.fetch_phrases()

    async def fetch_phrases(self):
        self.tracked_phrases = await self.db_manager.get_tracked_phrases()