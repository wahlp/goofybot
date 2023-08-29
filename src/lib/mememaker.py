import io
import logging
import textwrap
from enum import Enum

from PIL import Image, ImageDraw, ImageFont, ImageSequence

# todo: 
# add unicode text support

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class FontOptions(Enum):
    default = ("Futura", "caption.otf")
    comic_sans = ("Comic Sans", "Comic Sans MS Bold.ttf")

def calc_line_splitting(text, image_width, font):
    # init starting values for loop
    pixel_width = image_width
    max_char_per_line = len(text)

    draw = ImageDraw.Draw(Image.new("RGB", (image_width, 1), "white"))

    lines = textwrap.wrap(text, max_char_per_line)
    num_words = 0
    min_side_padding = 10 * 2
    while pixel_width + min_side_padding > image_width:
        # calc until we find a limit that fits the image width
        lines = textwrap.wrap(text, max_char_per_line)
        pixel_width = max(draw.textbbox((0, 0), line, font=font)[2] for line in lines)
        max_char_per_line = len(text.rsplit(' ', num_words)[0])
        num_words += 1

    return lines

def draw_multiple_line_text(
    image_width: int, 
    text: str, 
    font: ImageFont.FreeTypeFont, 
    text_color: str, 
):
    # https://stackoverflow.com/a/56205095

    lines = calc_line_splitting(text, image_width, font)

    # calculate starting height based on expected space required
    draw_dummy = ImageDraw.Draw(Image.new("RGB", (1, 1), "white"))
    line_heights = [draw_dummy.textbbox((0, 0), line, font=font)[3] for line in lines]
    text_height = max(line_heights) * len(line_heights)

    padding = 20
    new_img_height = text_height + padding * 2
    image = Image.new("RGB", (image_width, new_img_height), "white")
    draw = ImageDraw.Draw(image)

    y_text = padding - max(line_heights) // 16
    for line in lines:
        _, _, line_width, line_height = draw.textbbox((0, 0), line, font=font)
        draw.text(((image_width - line_width) / 2, y_text), 
                  line, font=font, fill=text_color)
        y_text += max(line_heights)

    if y_text > new_img_height:
        logger.warning(f'warning: drawn text has exceeded the height of the image. {image_width=}, {lines=}')

    return image

def add_caption(
    input_img: Image.Image, 
    text: str, 
    font: ImageFont.FreeTypeFont, 
    text_color: str, 
    transparency: bool
):
    img = draw_multiple_line_text(input_img.width, text, font, text_color)

    if transparency:
        mode = 'RGBA'
    else:
        mode = 'RGB'

    output_image = Image.new(mode, (input_img.width, input_img.height + img.height))
    output_image.paste(img, (0, 0))
    output_image.paste(input_img, (0, img.height))

    return output_image

def init_font(input_img_width: int, font: str, text: str):
    fontsize = input_img_width // 10

    font = ImageFont.truetype(f'./fonts/{FontOptions[font].value[1]}', fontsize)
    text_color = "black"

    return font, text_color

def add_text_to_image(image_data: bytes, text: str, font: str, transparency: bool):
    input_file = io.BytesIO(image_data)
    input_img = Image.open(input_file)

    font_object, text_color = init_font(input_img.width, font, text)
    output_image = add_caption(input_img, text, font_object, text_color, transparency)

    buffer = io.BytesIO()
    img_format = 'PNG' if transparency else 'JPEG'
    output_image.save(buffer, format=img_format)
    buffer.seek(0)
    return buffer

def add_text_to_gif(image_data: bytes, text: str, font: str, transparency: bool):
    # sort of broken with transparency
    # the frames sequentially get drawn on top of each other without clearing the old ones
    input_file = io.BytesIO(image_data)
    input_gif = Image.open(input_file)

    font_object, text_color = init_font(input_gif.width, font, text)

    frames: list[Image.Image] = []
    for frame in ImageSequence.Iterator(input_gif):
        frame_copy = frame.copy()
        output_image = add_caption(frame_copy, text, font_object, text_color, transparency)
        frames.append(output_image)
    
    buffer = io.BytesIO()
    frames[0].save(buffer, format="GIF", save_all=True, append_images=frames[1:], loop=0, duration=input_gif.info['duration'])
    buffer.seek(0)
    return buffer