import io
import textwrap

from PIL import Image, ImageDraw, ImageFont, ImageSequence

# todo: 
# add unicode text support

def draw_multiple_line_text(
    image_width: int, 
    text: str, 
    font: ImageFont.FreeTypeFont, 
    text_color: str, 
    text_width: int
):
    # https://stackoverflow.com/a/56205095

    padding = 20

    image_dummy = Image.new("RGB", (1, 1), "white")
    draw_dummy = ImageDraw.Draw(image_dummy)

    lines = textwrap.wrap(text, text_width)
    # calculate starting height based on expected space required
    line_heights = [draw_dummy.textbbox((0, 0), lines[0], font=font)[3] for line in lines ]
    text_height = sum(line_heights)

    new_img_height = text_height + padding * 2
    image = Image.new("RGB", (image_width, new_img_height), "white")
    draw = ImageDraw.Draw(image)

    y_text = padding - max(line_heights) // 16
    for line in lines:
        _, _, line_width, line_height = draw.textbbox((0, 0), line, font=font)
        draw.text(((image_width - line_width) / 2, y_text), 
                  line, font=font, fill=text_color)
        y_text += max(line_heights)

    return image

def add_caption(
    input_img: Image.Image, 
    text: str, 
    font: ImageFont.FreeTypeFont, 
    text_color: str, 
    text_width: int, 
    transparency: bool
):
    img = draw_multiple_line_text(input_img.width, text, font, text_color, text_width)

    if transparency:
        mode = 'RGBA'
    else:
        mode = 'RGB'

    output_image = Image.new(mode, (input_img.width, input_img.height + img.height))
    output_image.paste(img, (0, 0))
    output_image.paste(input_img, (0, img.height))

    return output_image

def init_text(input_img: Image.Image):
    fontsize = input_img.width // 10
    font = ImageFont.truetype("./fonts/caption.otf", fontsize)
    text_color = "black"
    text_width = input_img.width // 16

    return font, text_color, text_width

def add_text_to_image(image_data: bytes, text: str, transparency: bool):
    input_file = io.BytesIO(image_data)
    input_img = Image.open(input_file)

    font, text_color, text_width = init_text(input_img)
    output_image = add_caption(input_img, text, font, text_color, text_width, transparency)

    buffer = io.BytesIO()
    img_format = 'PNG' if transparency else 'JPG'
    output_image.save(buffer, format=img_format)
    buffer.seek(0)
    return buffer

def add_text_to_gif(image_data: bytes, text: str, transparency: bool):
    # sort of broken with transparency
    # the frames sequentially get drawn on top of each other without clearing the old ones
    input_file = io.BytesIO(image_data)
    input_gif = Image.open(input_file)

    font, text_color, text_width = init_text(input_gif)

    frames: list[Image.Image] = []
    for frame in ImageSequence.Iterator(input_gif):
        frame_copy = frame.copy()
        output_image = add_caption(frame_copy, text, font, text_color, text_width, transparency)
        frames.append(output_image)
    
    buffer = io.BytesIO()
    frames[0].save(buffer, format="GIF", save_all=True, append_images=frames[1:], loop=0, duration=input_gif.info['duration'])
    buffer.seek(0)
    return buffer