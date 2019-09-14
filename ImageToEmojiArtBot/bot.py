import discord
import json
from discord.ext import commands
from discord.ext.commands import Bot

client = commands.Bot(
    description="Emoji Bot 9000",
    command_prefix="!"
)

@client.command()
async def hello(ctx, arg: str):
    await ctx.send(arg)

if __name__ == "__main__":
    with open('secrets/client_login_info.json') as f:
        json_data = json.load(f)
    client.run(json_data.get('clientSecret'))