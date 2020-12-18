import json
import random
from discord.ext.commands import Bot, Context
from discord.ext import commands

client = commands.Bot(description="EULA Bot", command_prefix="!")
non_legally_binding_message = "(This is not legally binding advice.)"

@client.event
async def on_message(message):
    if message.author.id == 204343692960464896:
        await message.channel.send(non_legally_binding_message)

if __name__ == "__main__":
    with open("client_login_info.json") as f:
        json_data = json.load(f)
    client.run(json_data.get("clientSecret"))
