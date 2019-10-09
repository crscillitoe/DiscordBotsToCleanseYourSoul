import json
from discord.ext.commands import Bot, Context
from discord.ext import commands
from sclib import SoundcloudAPI, Track, Playlist

client = commands.Bot(
    description="Soundcloud Playlist Bot",
    command_prefix="!"
)
api = SoundcloudAPI()

@client.command()
async def shuffle(ctx: Context, playlist_url):
    playlist = api.resolve(playlist_url)

    for track in playlist.tracks:
        await ctx.send(f'-play {track.artist} - {track.title}')

@client.command()
async def test(ctx: Context, song):
    await ctx.send(f'-play {song}')

if __name__ == "__main__":
    with open('client_login_info.json') as f:
        json_data = json.load(f)
    client.run(json_data.get('clientSecret'))