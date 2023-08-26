import aiohttp
import io
import logging

import discord
from discord.ext import commands
from PIL import UnidentifiedImageError

from lib import mememaker
from lib.custombot import CustomBot


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
        # download the input
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as response:
                image_data = await response.read()

        # format and process the input
        input_file = io.BytesIO(image_data)
        output_image = mememaker.add_text_to_image(input_file, text)

        # format and send the output
        with io.BytesIO() as output:
            output_image.save(output, format="PNG")
            output.seek(0)
            output_file = discord.File(fp=output, filename="funny.png")
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