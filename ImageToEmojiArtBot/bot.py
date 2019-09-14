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
    string = convert_image_to_string(image).split('\n')
    for i in string:
        if i != '':
            await ctx.send(f'{i}')

if __name__ == "__main__":
    with open('client_login_info.json') as f:
        json_data = json.load(f)
    client.run(json_data.get('clientSecret'))