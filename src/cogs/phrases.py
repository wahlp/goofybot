import discord
from discord.ext import commands

from lib.custombot import CustomBot

class PhrasesCog(commands.GroupCog, name="phrases"):
    def __init__(self, bot: CustomBot):
        self.bot = bot
        super().__init__()

    @discord.app_commands.command(
        name='list',
        description='Show tracked phrases'
    )
    async def phrases_get(self, interaction: discord.Interaction):
        msg = '\n'.join(f'{x[0]} ({x[1]})' for x in self.bot.tracked_phrases)
        await interaction.response.send_message(msg)

    @discord.app_commands.command(
        name='update',
        description='Add or modify a tracked phrase'
    )
    @commands.is_owner()
    async def phrases_add(self, interaction: discord.Interaction, phrase: str, vanity_name: str):
        await self.bot.db_manager.upsert_tracked_phrase(phrase, vanity_name)
        await interaction.response.send_message(f'Added phrase: {phrase} ({vanity_name})')
        await self.bot.fetch_phrases()

    @discord.app_commands.command(
        name='delete',
        description='Delete a tracked phrase'
    )
    @commands.is_owner()
    async def phrases_delete(self, interaction: discord.Interaction, phrase: str):
        await self.bot.db_manager.delete_tracked_phrase(phrase)
        await interaction.response.send_message(f'Deleted phrase: {phrase}')
        await self.bot.fetch_phrases()

    async def phrase_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[discord.app_commands.Choice[str]]:
        return [
            discord.app_commands.Choice(name=vanity_name, value=phrase)
            for phrase, vanity_name in self.bot.tracked_phrases
            if current.lower() in vanity_name.lower()
        ]
    
    @discord.app_commands.command(
        name='stats',
        description='Show phrase usage'
    )
    @discord.app_commands.autocomplete(phrase=phrase_autocomplete)
    async def phrases_stats(
        self,
        interaction: discord.Interaction, 
        phrase: str, 
        user: discord.User = None
    ):
        if user is None:
            user = interaction.user

        data = await self.bot.db_manager.get_tracked_phrase_count(
            member_id=user.id, 
            phrase=phrase
        )

        if data:
            vanity_name, count = data[0]
            await interaction.response.send_message(
                f'{user.name} has said \"{vanity_name}\" a total of {count} times'
            )
        else:
            await interaction.response.send_message(
                "No data found (You queried for a phrase that isn't registered)"
            )

async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(PhrasesCog(bot))