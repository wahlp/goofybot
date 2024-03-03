import io
import logging
import os
import random
import string
import subprocess
import traceback
from typing import Optional

import aiohttp
import botocore
import discord
import mememaker
from discord.ext import commands
from PIL import UnidentifiedImageError
from slugify import slugify

from lib import aws
from lib.custombot import CustomBot
from lib.net import fetch_data

logger = logging.getLogger(__name__)

font_choices = [
    discord.app_commands.Choice(name=font_file_name.value[0], value=font_file_name.name)
    for font_file_name in mememaker.FontOptions
]

class MemeCog(commands.GroupCog, name="meme"):
    def __init__(self, bot: CustomBot):
        self.bot = bot
        super().__init__()

    @discord.app_commands.command(
        name='image',
        description='Add text to an image'
    )
    @discord.app_commands.describe(
        url='The URL of the input image',
        text='Caption for the output gif',
        font='Font for the text',
        transparency='Preserve transparency (defaults to False)',
    )
    @discord.app_commands.choices(
        font=font_choices
    )
    async def image(
        self, 
        interaction: discord.Interaction, 
        url: str, 
        text: str, 
        font: discord.app_commands.Choice[str] = None, 
        transparency: bool = False
    ):
        await interaction.response.defer()
        logger.info(f'{interaction.user} called for an image with parameters {url=}, {text=}')

        if font is None:
            font = font_choices[0]

        image_data = await fetch_data(url)
        buffer = mememaker.add_text_to_image(image_data, text, font.value, transparency)
        output_file_name = create_output_file_name(text, ext='png')
        output_file = discord.File(fp=buffer, filename=output_file_name)
        await interaction.followup.send(file=output_file)
    
    
    @discord.app_commands.command(
        name='size',
        description='Check the size of an image'
    )
    async def size(
        self, 
        interaction: discord.Interaction, 
        url: str
    ):
        await interaction.response.defer()

        if 'tenor.com' in url and not url.endswith('.gif'):
            url += '.gif'
        
        data = await fetch_data(url)
        size_in_kb = len(data) / 1024
        
        await interaction.followup.send(f"The size of this image is {size_in_kb:.2f} KB")

    def cooldown_for_everyone_but_me(interaction: discord.Interaction) -> Optional[discord.app_commands.Cooldown]:
        if str(interaction.user.id) == os.getenv('OWNER_USER_ID'):
            return None
        return discord.app_commands.Cooldown(1, 60.0)

    @discord.app_commands.command(
        name='gif',
        description='Add text to a gif'
    )
    @discord.app_commands.describe(
        url='The URL of the input gif',
        text='Caption for the output gif',
        compression='Smaller file size but needs more processing time (defaults to True)',
        speedup='Multiplies the speed of the output gif',
        font='Font for the text',
        compress_color='Smaller file size but fewer colors in the output (defaults to True)',
        transparency='Preserve transparency (defaults to False)',
    )
    @discord.app_commands.choices(
        font=font_choices
    )
    @discord.app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    async def gif(
        self, 
        interaction: discord.Interaction, 
        url: str, 
        text: str, 
        compression: bool = True,
        speedup: float = 1.0,
        font: discord.app_commands.Choice[str] = None, 
        compress_color: bool = True,
        transparency: bool = False
    ):  
        await interaction.response.defer()
        logger.info(f'{interaction.user} called for a gif with parameters {url=}, {text=}')
        
        if font is None:
            font = font_choices[0]
        
        if 'tenor.com' in url and not url.endswith('.gif'):
            url += '.gif'
            
        output_file_name = create_output_file_name(text, ext='gif')
        
        if os.getenv('ENVIRONMENT') == 'LOCAL':
            logger.info('processing gif locally')
            image_data = await fetch_data(url)
            buffer = mememaker.add_text_to_gif(image_data, text, font.value, transparency, speedup)

            if not compression:
                logger.info('uploading file to discord without compression')
                output_file = discord.File(fp=buffer, filename=output_file_name)
            else:
                image_bytes = buffer.read()
                logger.info(f'{len(image_bytes)} bytes image to be gifsicle-d')
                optimized_image_data = compress_gif(image_bytes, compress_color)
                logger.info('uploading compressed file to discord')
                output_file = discord.File(fp=io.BytesIO(optimized_image_data), filename=output_file_name)
            await interaction.followup.send(file=output_file)
        else:
            logger.info('processing gif via API')
            try:
                buffer = await aws.invoke_image_processing_lambda(url, text, font.value, transparency, speedup, compress_color)
                output_file = discord.File(fp=buffer, filename=output_file_name)
                await interaction.followup.send(file=output_file)
            except (
                aws.APITimeoutError, 
                botocore.exceptions.ReadTimeoutError
            ) as e:
                logger.info('gave up waiting for lambda invocation')
                await interaction.followup.send('The API ran out of processing time, the GIF you provided may have been too large in file size')
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                await interaction.followup.send('Something went wrong with the image API')


    async def cog_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, discord.app_commands.AppCommandError):
            if isinstance(error, discord.app_commands.errors.MissingPermissions):
                await interaction.response.send_message("You do not have the required permissions to run this command", ephemeral=True)
            elif isinstance(error, discord.app_commands.errors.CommandOnCooldown):
                await interaction.response.send_message(str(error), ephemeral=True)
        elif hasattr(error, 'original'):
            if isinstance(error.original, UnidentifiedImageError):
                await interaction.response.send_message("The content at the URL you provided could not be read as an image", ephemeral=True)
            elif isinstance(error.original, aiohttp.InvalidURL):
                await interaction.response.send_message("The URL you provided was invalid", ephemeral=True)
        else:
            await interaction.response.send_message("There was an error while running the command", ephemeral=True)
        raise error


async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(MemeCog(bot))


def create_output_file_name(text: str, ext: str):
    # https://stackoverflow.com/questions/13484726/safe-enough-8-character-short-unique-random-string
    alphabet = string.ascii_lowercase + string.digits
    random_str = ''.join(random.choices(alphabet, k=8))
    slugified_text = slugify(text, max_length=80, word_boundary=True)
    file_name = f'{slugified_text}-{random_str}.{ext}'
    return file_name


def compress_gif(image_bytes: bytes, compress_color: bool = True):
    cmd = [
        './gifsicle', '-O3',
        '--lossy=30',
        '-o', '/dev/stdout', 
        '--', '-'
    ]
    if compress_color:
        cmd[2:2] = ['--colors', '256']

    optimized_image = subprocess.run(
        cmd, 
        input=image_bytes, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE, 
        check=True
    )
    optimized_image_data = optimized_image.stdout
    return optimized_image_data