import logging
import os
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands, tasks

from lib import emojilib
from lib.custombot import CustomBot
from lib.envloader import load_env_vars

logging.Formatter.converter = lambda *args: datetime.now(tz=timezone(timedelta(hours=8))).timetuple()
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(module)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

if os.getenv('ENVIRONMENT') != 'LOCAL':
    logging.info('calling parameter store for environment variables')
    load_env_vars()
else:
    logging.info('using local environment variables')

target_channels = os.getenv('TARGET_CHANNEL')
if target_channels is None:
    logging.warning('target_channels not found')
    bot_reaction_channel_whitelist = []
else:
    bot_reaction_channel_whitelist = [int(x) for x in target_channels.split(',')]

bot = CustomBot()


# === Event listeners ===

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user}')

@bot.event
async def setup_hook():
    await bot.setup()
    ping_db.start()

@bot.event
async def on_message(message: discord.Message):
    if message.author != bot.user:
        # only let the bot react in one channel or it would get annoying fast
        if message.channel.id in bot_reaction_channel_whitelist:
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
    await bot.db_manager.add_reaction_record(
        reaction=payload.emoji.name, 
        member_id=payload.member.id, 
        message_id=payload.message_id, 
        timestamp=datetime.now()
    )

@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    
    await bot.db_manager.delete_reaction_record(
        reaction=payload.emoji.name, 
        member_id=member.id, 
        message_id=payload.message_id,
    )

    # msg = await client.get_channel(payload.channel_id).fetch_message(payload.message_id)
    # print(msg.jump_url)

@bot.event
async def on_guild_emojis_update(guild: discord.Guild, before: tuple[discord.Emoji], after: tuple[discord.Emoji]):
    # update the database when an emoji is renamed
    if len(before) == len(after):
        for e1, e2 in zip(before, after):
            if e1.name != e2.name:
                await bot.db_manager.rename_reaction_records(e1.name, e2.name)


# === Text commands ===

@bot.command()
@commands.is_owner()
async def sync(ctx, mode: str = '*'):
    if mode == '*':
        bot.tree.copy_global_to(guild=ctx.guild)
        synced_commands = await bot.tree.sync(guild=ctx.guild)
    elif mode == 'd':
        bot.tree.clear_commands(guild=None)
        synced_commands = await bot.tree.sync(guild=ctx.guild)
    
    logging.info(f'synced commands: {len(synced_commands)}')
    await ctx.send('Command tree synced')

@bot.command()
@commands.is_owner()
async def reload(ctx):
    await bot.reload_cogs()
    await ctx.send('Reloaded cogs')


@bot.command()
async def ping(ctx):
    await ctx.send(f'Pong! ({round(bot.latency * 1000)} ms)')


# === Tasks (crewmate from among us reference) ===

@tasks.loop(hours=4)
async def ping_db():
    logging.info('pinging db')
    await bot.db_manager.ping()


if __name__ == '__main__':
    bot.run(os.getenv("DISCORD_TOKEN"))
