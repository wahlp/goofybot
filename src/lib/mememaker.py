import textwrap
from PIL import Image, ImageDraw, ImageFont

# todo: 
# add transparency support for png
# add gif support
# add unicode text support

def draw_multiple_line_text(image_width, text, font, text_color, text_width):
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
    # print(f'starting line_height={y_text}')
    for line in lines:
        _, _, line_width, line_height = draw.textbbox((0, 0), line, font=font)
        draw.text(((image_width - line_width) / 2, y_text), 
                  line, font=font, fill=text_color)
        y_text += max(line_heights)
        # print(f'{y_text=}')

    # print(f'{new_img_height=}')
    return image

def add_text_to_image(input_file, text):
    input_img = Image.open(input_file)

    fontsize = input_img.width // 10
    font = ImageFont.truetype("./fonts/caption.otf", fontsize)
    text_color = "black"
    max_line_length = input_img.width // 16

    # print(f'{fontsize=}')
    # print(f'{max_line_length=}')

    img = draw_multiple_line_text(input_img.width, text, font, text_color, text_width=max_line_length)

    output_image = Image.new('RGB', (input_img.width, input_img.height + img.height))
    output_image.paste(img, (0, 0))
    output_image.paste(input_img, (0, img.height))

    return output_image
