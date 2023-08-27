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

class MemeCog(commands.GroupCog, name="meme"):
    def __init__(self, bot: CustomBot):
        self.bot = bot
        super().__init__()

    @discord.app_commands.command(
        name='image',
        description='Add text to image'
    )
    async def image(self, interaction: discord.Interaction, file_url: str, text: str):
        image_data = await fetch_data(file_url)
        buffer = mememaker.add_text_to_image(image_data, text)
        output_file = discord.File(fp=buffer, filename="funny.png")
        await interaction.response.send_message(file=output_file)

    
    @discord.app_commands.command(
        name='gif',
        description='Add text to gif'
    )
    async def gif(self, interaction: discord.Interaction, file_url: str, text: str):
        image_data = await fetch_data(file_url)
        buffer = mememaker.add_text_to_gif(image_data, text)
        output_file = discord.File(fp=buffer, filename="funny.gif")
        await interaction.response.send_message(file=output_file)


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