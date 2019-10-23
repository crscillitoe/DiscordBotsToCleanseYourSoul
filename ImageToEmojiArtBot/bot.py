import discord
import json
import requests
from io import BytesIO
from pixel_processor import convert_image_to_string, convert_image_to_emoji_list
from image_processor import create_opencv_image_from_url
from discord.ext import commands
from discord.ext.commands import Bot, Context
from typing import *
import numpy as np
import cv2

client = commands.Bot(
    description="Emoji Bot 9000",
    command_prefix="!"
)

@client.command()
async def build_dict(ctx: Context, emoji_str: str):
    print(client.emojis)
    await ctx.send('processed')

@client.command()
async def emojify(ctx: Context, image_url: str):
    width = 50
    height = 50
    emoji_width = 50
    emoji_height = 50
    req: Response = requests.get(image_url)
    if req.status_code != 200:
        raise Exception
    image = create_opencv_image_from_url(bytearray(req.content), width, height)
    emojis = convert_image_to_emoji_list(image)

    loaded_images = {}
    complete_image = None
    for row in emojis:
        row_image = None
        for emoji in row:
            if emoji not in loaded_images:
                print(f'/svgs/{emoji}.svg.png')
                image = cv2.imread(f"/svgs/{emoji}.svg.png", cv2.IMREAD_COLOR)
                loaded_images[emoji] = cv2.resize(image, (emoji_width, emoji_height), interpolation=cv2.INTER_AREA)

            # Now we know we're in the cache
            if row_image is None:
                row_image = loaded_images[emoji]
            else:
                row_image = np.vstack((row_image, loaded_images[emoji]))
        if complete_image is None:
            complete_image = row_image
        else:
            complete_image = np.hstack((complete_image, row_image))

    success, encoded_image = cv2.imencode('.png', complete_image)
    image_bytes = encoded_image.tobytes()
    await ctx.send(file=discord.File(BytesIO(image_bytes), 'emojified.png'))

@client.command()
async def copy_image(ctx: Context, image_url: str):
    req: Response = requests.get(image_url)
    await ctx.send(file=discord.File(BytesIO(req.content), 'emojified.png'))

def break_into_parts(string: str, input_separator: str, max_message_len: int, output_separator: str = '\n') -> List[str]:
    """
    Given an input string, split on the given split character and return
    an array of batches such that each batch's string length is as close to
    max_message_len as possible without exceeding it.
    """
    split_string = string.split(input_separator)[:-1]
    batch_array = []
    curr_batch_line = ''
    curr_len = 0
    for message_line in split_string:
        if curr_len + len(message_line) < max_message_len - len(output_separator):
            curr_batch_line += message_line + output_separator
            curr_len += len(message_line) + len(output_separator)
        else:
            batch_array.append(curr_batch_line)
            curr_batch_line = message_line + output_separator
            curr_len = len(message_line) + len(output_separator)

    curr_batch_split = curr_batch_line.split(output_separator)[:-1]
    prev_batch_split = batch_array[-1]
    prev_batch_split = prev_batch_split.split(output_separator)[:-1]
    if len(curr_batch_split) == 1 and len(curr_batch_line) + len(prev_batch_split[-1]) < max_message_len:
        batch_array[-1] = "\n".join(prev_batch_split[:-1])
        curr_batch_line = prev_batch_split[-1] + output_separator + curr_batch_line

    batch_array.append(curr_batch_line)

    return batch_array

if __name__ == "__main__":
    with open('client_login_info.json') as f:
        json_data = json.load(f)
    client.run(json_data.get('clientSecret'))