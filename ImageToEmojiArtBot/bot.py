import discord
import json
import requests
from io import BytesIO
from pixel_processor import convert_pixel_to_emoji
from pixel_processor import convert_image_to_string
from image_processor import create_opencv_image_from_url
from discord.ext import commands
from discord.ext.commands import Bot, Context
from typing import *

client = commands.Bot(
    description="Emoji Bot 9000",
    command_prefix="!"
)

@client.command()
async def build_dict(ctx: Context, emoji_str: str):
    print(client.emojis)
    await ctx.send('processed')

@client.command()
async def get_emoji(ctx: Context, red: str, green: str, blue: str):
    try:
        red_int: int   = int(red)
        green_int: int = int(green)
        blue_int: int  = int(blue)
    except:
        await ctx.send('Those aren\'t 3 numbers you dumbass')

    await ctx.send(convert_pixel_to_emoji(red_int, green_int, blue_int))

@client.command()
async def emojify(ctx: Context, image_url: str, width: int = 25, height: int = 25):
    try:
        req: Response = requests.get(image_url)
        if req.status_code != 200:
            raise Exception
        image = create_opencv_image_from_url(bytearray(req.content), width, height)
        string = convert_image_to_string(image)
        string_batch = break_into_parts(string, '|', 1000)
        await ctx.send(f'Batched image into {len(string_batch)} batches: {[len(i) for i in string_batch]}')
        for i in string_batch:
            if i != '':
                await ctx.send(f'{i}')
    except:
        await ctx.send('Image download failed')

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
    prev_batch_split = batch_array[-1].split(output_separator)[:-1]
    if len(curr_batch_split) == 1 and len(curr_batch_line) + len(prev_batch_split[-1]) < max_message_len:
        batch_array[-1] = "\n".join(prev_batch_split[:-1])
        curr_batch_line = prev_batch_split[-1] + output_separator + curr_batch_line

    batch_array.append(curr_batch_line)

    return batch_array

if __name__ == "__main__":
    with open('secrets/client_login_info.json') as f:
        json_data = json.load(f)
    client.run(json_data.get('clientSecret'))