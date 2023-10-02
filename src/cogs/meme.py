import aiohttp
import io
import logging
import subprocess
import os
import traceback

import discord
from discord.ext import commands
from PIL import UnidentifiedImageError

from lib import mememaker
from lib.custombot import CustomBot
from lib.net import fetch_data


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
        transparency='Specifies if you want to preserve transparency (Optional, defaults to False)'
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
        output_file = discord.File(fp=buffer, filename="funny.png")
        await interaction.followup.send(file=output_file)
    

    @discord.app_commands.command(
        name='gif',
        description='Add text to a gif'
    )
    @discord.app_commands.describe(
        url='The URL of the input gif',
        transparency='Specifies if you want to preserve transparency (Optional, defaults to False)'
    )
    @discord.app_commands.choices(
        font=font_choices
    )
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def gif(
        self, 
        interaction: discord.Interaction, 
        url: str, 
        text: str, 
        font: discord.app_commands.Choice[str] = None, 
        transparency: bool = False
    ):  
        await interaction.response.defer()
        logger.info(f'{interaction.user} called for a gif with parameters {url=}, {text=}')
        
        if font is None:
            font = font_choices[0]
        
        if 'tenor.com' in url and not url.endswith('.gif'):
            url += '.gif'
        
        if os.getenv('ENVIRONMENT') == 'LOCAL':
            logger.info('processing gif locally')
            image_data = await fetch_data(url)
            buffer = mememaker.add_text_to_gif(image_data, text, font.value, transparency)
            image_bytes = buffer.read()

            cmd = ['gifsicle', '-O3', '--colors', '256', '--lossy=30', '-o', '/dev/stdout', '--', '-']
            optimized_image = subprocess.run(
                cmd, 
                input=image_bytes, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                check=True
            )
            optimized_image_data = optimized_image.stdout
            
            output_file = discord.File(fp=io.BytesIO(optimized_image_data), filename="funny.gif")
            await interaction.followup.send(file=output_file)
        else:
            logger.info('processing gif via API')
            try:
                buffer = await mememaker.call_api(url, text, font.value, transparency)
            except Exception as e:
                # logger.error(e)
                traceback.print_exception(type(e), e, e.__traceback__)
                await interaction.followup.send('Something went wrong with the image API')
                return
            
            output_file = discord.File(fp=buffer, filename="funny.gif")


    async def cog_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, discord.app_commands.errors.MissingPermissions):
            await interaction.response.send_message("You do not have the required permissions to run this command", ephemeral=True)
        if isinstance(error.original, UnidentifiedImageError):
            await interaction.response.send_message("The content at the URL you provided could not be read as an image", ephemeral=True)
        elif isinstance(error.original, aiohttp.InvalidURL):
            await interaction.response.send_message("The URL you provided was invalid", ephemeral=True)
        else:
            await interaction.response.send_message("There was an error while running the command", ephemeral=True)
            # logger.error(error)
            raise error


async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(MemeCog(bot))