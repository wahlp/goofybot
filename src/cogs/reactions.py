import discord
from discord.ext import commands

from lib import emojilib
from lib.custombot import CustomBot


class Reactions(commands.GroupCog, name="reactions"):
    def __init__(self, bot: CustomBot):
        self.bot = bot
        super().__init__()

    @discord.app_commands.command(
        name='stats',
        description='Show total reaction stats based on all users'
    )
    async def stats_global(self, interaction: discord.Interaction, limit: int = 10):
        res = await self.bot.db_manager.get_stats(
            limit=limit
        )

        if not res:
            await interaction.response.send_message('No reactions recorded')
        else:    
            msg = format_stats(interaction, res)
            await interaction.response.send_message(msg)


    @discord.app_commands.command(
        name='fav',
        description='Show a user\'s most used reactions'
    )
    @discord.app_commands.describe(user='Leaving this empty field assumes you want to run this command for yourself')
    async def stats_user(self, interaction: discord.Interaction, user: discord.User = None, limit: int = 10):
        if user is None:
            user = interaction.user
            
        res = await self.bot.db_manager.get_stats(
            member_id=user.id,
            limit=limit
        )

        if not res:
            await interaction.response.send_message('No reactions recorded for that user')
        else:    
            msg = format_stats(interaction, res)
            await interaction.response.send_message(msg)


async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(Reactions(bot))


def format_stats(ctx, lst: list[tuple[str, int]]):
    lines = []
    for emoji_name, count in lst:
        parsed_emoji = emoji_name
        if emojilib.is_custom_emoji(emoji_name):
            e = discord.utils.find(lambda x: x.name == emoji_name, ctx.guild.emojis)
            if e is not None and e.is_usable:
                parsed_emoji = str(e)
        lines.append(f'{parsed_emoji}: {count}')

    return '\n'.join(lines)