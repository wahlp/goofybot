import aiohttp
import io
import logging

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
        
        image_data = await fetch_data(url)
        buffer = mememaker.add_text_to_gif(image_data, text, font.value, transparency)
        output_file = discord.File(fp=buffer, filename="funny.gif")
        await interaction.followup.send(file=output_file)


    async def cog_app_command_error(self, interaction: discord.Interaction, error):
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