import logging

import discord
from discord.ext import commands

from lib.custombot import CustomBot

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class CountersCog(commands.GroupCog, name="counters"):
    def __init__(self, bot: CustomBot):
        self.bot = bot
        super().__init__()

    @discord.app_commands.command(
        name='create',
        description='Create a new counter'
    )
    @discord.app_commands.describe(
        name='How the counter will be identified in future commands',
        message=(
            'The message to be shown when the counter is updated. ' 
            '`{}` represents where the value of the count will appear in the message'
        )
    )
    async def create(
        self, 
        interaction: discord.Interaction, 
        name: str,
        message: str
    ):
        if '{}' not in message:
            await interaction.response.send_message(
                'The message requires a `{}` somewhere in it, counter was not created',
                ephemeral=True
            )
            return
        
        success = await self.bot.db_manager.create_counter(name, message)
        if success:
            msg = f'Counter created: {name}'
        else:
            msg = f'Counter could not be created, maybe it already exists'
        
        await interaction.response.send_message(msg)
        await self.bot.fetch_counters()


    async def name_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[discord.app_commands.Choice[str]]:
        return [
            discord.app_commands.Choice(name=counter_name, value=counter_name)
            for counter_name in self.bot.counter_names
            if current.lower() in counter_name.lower()
        ]

    
    @discord.app_commands.command(
        name='increment',
        description='+1 to a counter'
    )
    @discord.app_commands.describe(
        name='Name of the counter',
        instigator='The @ of the person who caused the counter to go up (Optional, defaults to nobody)'
    )
    @discord.app_commands.autocomplete(name=name_autocomplete)
    async def increment(
        self, 
        interaction: discord.Interaction, 
        name: str,
        instigator: discord.User = None
    ):
        if isinstance(instigator, discord.User):
            instigator_id = instigator.id
        else:
            instigator_id = None
            
        await self.bot.db_manager.record_counter_incident(name, instigator_id)
        res = await self.bot.db_manager.show_counter_value(name)
        if res is not None:
            [[count, msg]] = res
            await interaction.response.send_message(msg.format(count))
        else:
            await interaction.response.send_message('The query yielded no results :sob:')

    

    @discord.app_commands.command(
        name='show',
        description='Show the details of a particular counter'
    )
    @discord.app_commands.autocomplete(name=name_autocomplete)
    async def show(
        self, 
        interaction: discord.Interaction, 
        name: str
    ):
        count, msg = await self.bot.db_manager.show_counter_value(name)
        await interaction.response.send_message(msg.format(count))
       


async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(CountersCog(bot))