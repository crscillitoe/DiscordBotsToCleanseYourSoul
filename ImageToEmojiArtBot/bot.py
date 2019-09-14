import discord
import json
import requests
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
async def get_emoji(ctx: Context, red: str, green: str, blue: str):
    try:
        red_int: int   = int(red)
        green_int: int = int(green)
        blue_int: int  = int(blue)
    except:
        await ctx.send('Those aren\'t 3 numbers you dumbass')

    await ctx.send(convert_pixel_to_emoji(red_int, green_int, blue_int))

@client.command()
async def emojify(ctx: Context, image_url: str):
    try:
        req: Response = requests.get(image_url)
        if req.status_code != 200:
            raise Exception
    except:
        await ctx.send('Image download failed')
    image = create_opencv_image_from_url(bytearray(req.content))
    string = convert_image_to_string(image)
    string_batch = break_into_parts(string, '\n', 2000)
    for i in string_batch:
        print(len(i))
        if i != '':
            await ctx.send(f'{i}')

def break_into_parts(string: str, split_character: str, max_message_len: int) -> List[str]:
    """
    Given an input string, split on the given split character and return
    an array of batches such that each batch's string length is as close to
    max_message_len as possible without exceeding it.
    """
    split_string = string.split(split_character)
    batch_array = []
    curr_batch_line = ''
    curr_len = 0
    for message_line in split_string:
        print(message_line)
        if curr_len + len(message_line) < max_message_len - 2:
            curr_batch_line += message_line + '\n'
            curr_len += len(message_line) + 1
        else:
            batch_array.append(curr_batch_line)
            curr_batch_line = message_line + '\n'
            curr_len = len(message_line) + 1

    return batch_array

if __name__ == "__main__":
    with open('secrets/client_login_info.json') as f:
        json_data = json.load(f)
    client.run(json_data.get('clientSecret'))