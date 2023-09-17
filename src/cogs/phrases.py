import discord
from discord.ext import commands

from lib.custombot import CustomBot

class PhrasesCog(commands.GroupCog, name="phrases"):
    def __init__(self, bot: CustomBot):
        self.bot = bot
        super().__init__()

    def find_phrase_tuple(self, phrase: str = None, vanity_name: str = None):
        if phrase is not None:
            return next((x for x in self.bot.tracked_phrases if phrase == x[0]), (None, None))
        if vanity_name is not None:
            return next((x for x in self.bot.tracked_phrases if vanity_name == x[1]), (None, None))

    @discord.app_commands.command(
        name='list',
        description='Show tracked phrases'
    )
    async def phrases_get(self, interaction: discord.Interaction):
        msg = '\n'.join(f'{x[0]} ({x[1]})' for x in self.bot.tracked_phrases)
        await interaction.response.send_message(msg, ephemeral=True)

    @discord.app_commands.command(
        name='update',
        description='Add or modify a tracked phrase (Admin only)'
    )
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def phrases_add(self, interaction: discord.Interaction, phrase: str, vanity_name: str):
        result = await self.bot.db_manager.upsert_tracked_phrase(phrase, vanity_name)
        if result:
            await interaction.response.send_message(f'Added phrase with vanity name: {vanity_name}')
        else:
            await interaction.response.send_message('Did not add phrase')
        await self.bot.fetch_phrases()

    async def vanity_name_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[discord.app_commands.Choice[str]]:
        return [
            discord.app_commands.Choice(name=vanity_name, value=vanity_name)
            for phrase, vanity_name in self.bot.tracked_phrases
            if current.lower() in vanity_name.lower()
        ]
    
    @discord.app_commands.command(
        name='delete',
        description='Delete a tracked phrase (Admin only)'
    )
    @discord.app_commands.autocomplete(vanity_name=vanity_name_autocomplete)
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def phrases_delete(self, interaction: discord.Interaction, vanity_name: str):
        phrase, _ = self.find_phrase_tuple(vanity_name=vanity_name)
        result = await self.bot.db_manager.delete_tracked_phrase(phrase)
        if result:
            await interaction.response.send_message(f'Deleted phrase: {vanity_name}')
        else:
            await interaction.response.send_message('Did not delete phrase')
        await self.bot.fetch_phrases()
    
    @discord.app_commands.command(
        name='stats',
        description='Show phrase usage'
    )
    @discord.app_commands.autocomplete(vanity_name=vanity_name_autocomplete)
    async def phrases_stats(
        self,
        interaction: discord.Interaction, 
        vanity_name: str, 
        user: discord.User = None
    ):
        if user is None:
            user = interaction.user

        phrase, _ = self.find_phrase_tuple(vanity_name=vanity_name)
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

    async def cog_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, discord.app_commands.errors.MissingPermissions):
            await interaction.response.send_message("You do not have the required permissions to run this command", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(PhrasesCog(bot))