import logging
import os
from datetime import datetime, timezone, timedelta

import discord
from discord.ext import commands, tasks

from lib import db, emojilib


logging.Formatter.converter = lambda *args: datetime.now(tz=timezone(timedelta(hours=8))).timetuple()
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(module)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

target_channel = int(os.getenv('TARGET_CHANNEL'))


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


bot = CustomBot()


# === Event listeners ===

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')

@bot.event
async def setup_hook():
    await bot.setup()
    declare_dependent_commands()
    await bot.load_extension('cogs.sample')

@bot.event
async def on_message(message: discord.Message):
    if message.author != bot.user:
        # only let the bot react in one channel or it would get annoying fast
        if message.channel.id == target_channel:
            emoji_list = emojilib.get_relevant_emojis(message.content)
            for emoji in emoji_list:
                await message.add_reaction(emoji)

        for phrase, vanity_name in bot.tracked_phrases:
            num_occurrences = message.content.lower().count(phrase)
            if num_occurrences >= 1:
                await bot.db_manager.update_tracked_phrase_count(message.author.id, phrase, num_occurrences)

    await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    emoji = payload.emoji.name
    member = payload.member
    message_id = payload.message_id
    reaction_timestamp = datetime.now()
    
    await bot.db_manager.add_reaction_record(emoji, member.id, message_id, reaction_timestamp)

@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    emoji = payload.emoji.name
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    message_id = payload.message_id
    
    await bot.db_manager.delete_reaction_record(emoji, member.id, message_id)

    # msg = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
    # print(msg.jump_url)

@bot.event
async def on_guild_emojis_update(guild: discord.Guild, before: tuple[discord.Emoji], after: tuple[discord.Emoji]):
    # update the database when an emoji is renamed
    if len(before) == len(after):
        for e1, e2 in zip(before, after):
            if e1.name != e2.name:
                await bot.db_manager.rename_reaction_records(e1.name, e2.name)


# === Slash commands ===

# @bot.tree.command(
#     name='say',
#     description='trying out slash commands'
# )
# @discord.app_commands.choices(action=[
#     discord.app_commands.Choice(name='hello', value='Hello!'),
#     discord.app_commands.Choice(name='goodbye', value='Goodbye!'),
# ])
# async def hello(interaction: discord.Interaction, action: discord.app_commands.Choice[str]):
#     await interaction.response.send_message(action.value)

@bot.tree.command(
    name='stats',
    description='Show emoji reaction stats'
)
async def stats_slash(interaction: discord.Interaction, user: discord.User = None, limit: int = 10):
    if user is None:
        user = interaction.user

    res = await bot.db_manager.get_stats(
        member_id=user.id, 
        limit=limit
    )

    msg = format_stats(interaction, res)
    await interaction.response.send_message(msg)

# @bot.tree.command(
#     name='optout',
#     description='Opt out of the bot\'s tracking'
# )
# async def optout(interaction: discord.Interaction):
#     await bot.db_manager.add_to_opt_out_list(interaction.user)


# class GroupTest(commands.GroupCog, group_name='group'):
#     def __init__(self, bot: CustomBot):
#         self.bot = bot

#     @discord.app_commands.command(
#         name='hi',
#         description='Say hi'
#     )
#     async def say_hi(self, interaction: discord.Interaction):
#         await interaction.response.send_message('Hi!')



phrases = discord.app_commands.Group(name='phrases', description="Manage tracked phrases")
bot.tree.add_command(phrases)

@phrases.command(
    name='list',
    description='Show tracked phrases'
)
async def phrases_get(interaction: discord.Interaction):
    msg = '\n'.join(f'{x[0]} ({x[1]})' for x in bot.tracked_phrases)
    await interaction.response.send_message(msg)

@phrases.command(
    name='update',
    description='Add or modify a tracked phrase'
)
@commands.is_owner()
async def phrases_add(interaction: discord.Interaction, phrase: str, vanity_name: str):
    await bot.db_manager.upsert_tracked_phrase(phrase, vanity_name)
    await interaction.response.send_message(f'Added phrase: {phrase} ({vanity_name})')
    await bot.fetch_phrases()

@phrases.command(
    name='delete',
    description='Delete a tracked phrase'
)
@commands.is_owner()
async def phrases_delete(interaction: discord.Interaction, phrase: str):
    await bot.db_manager.delete_tracked_phrase(phrase)
    await interaction.response.send_message(f'Deleted phrase: {phrase}')
    await bot.fetch_phrases()


def declare_dependent_commands():
    @phrases.command(
        name='stats',
        description='Show phrase usage'
    )
    @discord.app_commands.choices(phrase=[
        discord.app_commands.Choice(name=vanity_name, value=phrase)
        for phrase, vanity_name in bot.tracked_phrases
    ])
    async def phrases_stats(
        interaction: discord.Interaction, 
        phrase: discord.app_commands.Choice[str], 
        user: discord.User = None
    ):
        if user is None:
            user = interaction.user

        data = await bot.db_manager.get_tracked_phrase_count(
            member_id=user.id, 
            phrase=phrase.value
        )

        if data:
            vanity_name, count = data[0]
            await interaction.response.send_message(
                f'{user.name} has said \"{vanity_name}\" a total of {count} times'
            )
        else:
            await interaction.response.send_message(
                "No data found (You somehow managed to query for a phrase that isn't registered)"
            )


# === Text commands ===

@bot.command()
@commands.is_owner()
async def sync(ctx):
    # declare_dependent_commands()
    bot.tree.copy_global_to(guild=ctx.guild)
    synced_commands = await bot.tree.sync(guild=ctx.guild)
    # bot.tree.clear_commands(guild=None)
    # synced_commands = await bot.tree.sync()
    print(synced_commands)


    await ctx.send('Command tree synced')

@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! ({round(bot.latency * 1000)} ms)')



@bot.command()
async def stats(ctx):
    '''Show collective stats from all users
    '''
    res = await bot.db_manager.get_stats(
        # member_id=ctx.message.author.id, 
        limit=10
    )

    msg = format_stats(ctx, res)

    await ctx.send(msg)

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


# === Tasks (crewmate from among us reference) ===

@tasks.loop(hours=4)
async def ping_db():
    logging.info('pinging db')
    db.ping()


if __name__ == '__main__':
    bot.run(os.getenv("DISCORD_TOKEN"))
