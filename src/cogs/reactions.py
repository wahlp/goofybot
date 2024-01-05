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
    @discord.app_commands.describe(
        time_range='Number of days to search across',
        limit='Number of top reactions to show',
    )
    async def stats_global(
        self, 
        interaction: discord.Interaction, 
        time_range: int = 7,
        limit: int = 10,
    ):
        res = await self.bot.db_manager.get_stats(
            time_range=time_range,
            limit=limit,
        )

        if not res:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=f'No reactions recorded in the last {time_range} days'
                )
            )
        else:    
            msg = format_stats(interaction, res)
            embed = create_embed(
                user_name='everyone',
                time_range=time_range,
                description=msg
            )
            await interaction.response.send_message(embed=embed)


    @discord.app_commands.command(
        name='fav',
        description='Show a user\'s most used reactions'
    )
    @discord.app_commands.describe(
        user='Leaving this empty field assumes you want to run this command for yourself',
        time_range='Number of days to search across',
        limit='Number of top reactions to show',
    )
    async def stats_user(
        self, 
        interaction: discord.Interaction, 
        user: discord.User = None, 
        time_range: int = 7,
        limit: int = 10
    ):
        if user is None:
            user = interaction.user
            
        res = await self.bot.db_manager.get_stats(
            member_id=user.id,
            time_range=time_range,
            limit=limit,
        )

        if not res:
            await interaction.response.send_message(
                embed=discord.Embed(
                    description=f'No reactions recorded for {user.mention} in the last {time_range} days'
                )
            )
        else:    
            msg = format_stats(interaction, res)
            embed = create_embed(
                user_name=user.name,
                time_range=time_range,
                description=msg
            )
            await interaction.response.send_message(embed=embed)


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

def create_embed(user_name: str, time_range: int, description: str):
    embed = discord.Embed(
        title=f'Top reactions:\n{user_name}, last {time_range} days',
        description=description
    )
    return embed
