import json
import random
from discord.ext.commands import Bot, Context
from discord.ext import commands
import discord
import sqlite3
from discord import NoMoreItems
from tabulate import tabulate
import math

ranked_counting_channel_id = 771783255375478816

good_emojis = ["🆒", "🧠", "🥳", "💯", "👌", "🤏", "🙏", "♿", "🎉", "😎", "💎"]

bad_emojis = ["🆘", "🤡", "🤨", "😒", "🤢", "🤮", "👨‍🦽", "🐒", "⁉"]

client = commands.Bot(description="Count Bot", command_prefix="!")
print("running")


@client.event
async def on_ready():
    with sqlite3.connect("my_database.db") as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS Counters
                               (ID INT NOT NULL,
                                Name TEXT NOT NULL
                                )"""
        )

        conn.execute(
            """CREATE TABLE IF NOT EXISTS Errors
                               (ID INTEGER PRIMARY KEY,
                                UserID INT DEFAULT 0,
                                SentMessage TEXT NOT NULL,
                                ExpectedMessage TEXT NOT NULL,
                                Date TEXT DEFAULT CURRENT_TIMESTAMP
                                )"""
        )

        conn.execute(
            """CREATE TABLE IF NOT EXISTS Counts
                               (ID INTEGER PRIMARY KEY,
                                UserID INT DEFAULT 0,
                                SentMessage TEXT NOT NULL,
                                Date TEXT DEFAULT CURRENT_TIMESTAMP
                                )"""
        )

        conn.execute(
            """CREATE TABLE IF NOT EXISTS CurrentCount
                               (CountTrueValue INT NOT NULL)"""
        )

    print("Logged in as " + client.user.name + " (ID:" + str(client.user.id) + ")")
    print("--------")
    print("Current Discord.py Version: {}".format(discord.__version__))
    print("--------")
    print("Use this link to invite {}:".format(client.user.name))
    print(
        "https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8".format(
            client.user.id
        )
    )


def get_count():
    with sqlite3.connect("my_database.db") as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT CountTrueValue FROM CurrentCount LIMIT 1
            """
        )
        rows = cur.fetchall()

        if len(rows) == 0:
            return 1
        return int(rows[0][0])


@client.event
async def on_message(message):
    if message.channel.id == ranked_counting_channel_id:
        # THIS IS NOT A DRILL, WE ARE COUNTING
        current_count = get_count()
        expected_count = compute_correct_fizzbuzz(current_count + 1)
        with sqlite3.connect("my_database.db") as conn:
            cur = conn.cursor()
            if message.content == expected_count:
                # success
                cur.execute(
                    """INSERT INTO Counts (UserID, SentMessage)
                                        VALUES (?, ?)""",
                    (
                        message.author.id,
                        message.content,
                    ),
                )
                await message.add_reaction("✅")

                if message.content.startswith("fizz"):
                    await message.add_reaction("🥂")
                if message.content.endswith("buzz"):
                    await message.add_reaction("🐝")

                for i in range(5):
                    await message.add_reaction(random.choice(good_emojis))
            else:
                # failure
                cur.execute(
                    """INSERT INTO Errors (UserID, SentMessage, ExpectedMessage)
                                        VALUES (?, ?, ?)""",
                    (
                        message.author.id,
                        message.content,
                        expected_count,
                    ),
                )
                await message.add_reaction("❌")
                for i in range(5):
                    await message.add_reaction(random.choice(bad_emojis))

        await set_count(message, current_count + 1)

    if message.author.id == 82969926125490176 and message.content == "!generate_db":
        await message.channel.send(
            "Re-generating counting database from channel {}".format(
                ranked_counting_channel_id
            )
        )
        await generate_db(message)
    for role in message.author.roles:
        if role.id == 771860536140759061:
            taunt = random.randint(69, 73)
            if taunt == 69:
                await message.add_reaction("💩")


async def generate_db(ctx):
    channel = discord.utils.get(ctx.guild.text_channels, id=ranked_counting_channel_id)
    messages = channel.history(limit=None)
    stack = []
    while True:
        try:
            message = await messages.next()
            parsed = {
                "date": message.created_at,
                "author": message.author,
                "edited": message.edited_at,
                "content": message.content,
            }
            stack.append(parsed)
        except NoMoreItems:
            break

    with sqlite3.connect("my_database.db") as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM Counters WHERE 1=1")
        cur.execute("DELETE FROM Errors WHERE 1=1")
        cur.execute("DELETE FROM Counts WHERE 1=1")
        seen_authors = []
        current_count = 1
        error_count = 0
        for message in reversed(stack):
            if message["author"].id not in seen_authors:
                await ctx.channel.send(
                    "Found new counter! ID: {}, Name: {}".format(
                        message["author"].id, message["author"].name
                    )
                )
                cur.execute(
                    """INSERT INTO Counters (ID, Name)
                                        VALUES (?, ?)""",
                    (message["author"].id, message["author"].name),
                )

                seen_authors.append(message["author"].id)

            expected_result = compute_correct_fizzbuzz(current_count)
            if current_count == 100 or current_count == 101:
                # Curse you, ethan
                current_count += 1
                continue
            if message["content"] != expected_result or message["edited"] != None:
                error_count += 1
                # ERROR!
                cur.execute(
                    """INSERT INTO Errors (UserID, SentMessage, ExpectedMessage, Date)
                                        VALUES (?, ?, ?, ?)""",
                    (
                        message["author"].id,
                        "Unknown",
                        expected_result,
                        message["date"],
                    ),
                )
            else:
                # Good Count!
                cur.execute(
                    """INSERT INTO Counts (UserID, SentMessage, Date)
                                        VALUES (?, ?, ?)""",
                    (
                        message["author"].id,
                        message["content"],
                        message["date"],
                    ),
                )
            current_count += 1

        await ctx.channel.send(
            "Finished importing data! Found {} messages from {} counters, with {} errors!".format(
                current_count - 1, len(seen_authors), error_count
            )
        )

    await set_count(ctx, current_count - 1, True)


async def set_count(ctx, n, log=False):
    with sqlite3.connect("my_database.db") as conn:
        cur = conn.cursor()

        cur.execute(
            """
            SELECT CountTrueValue FROM CurrentCount LIMIT 1
            """
        )
        rows = cur.fetchall()
        if len(rows) == 0:
            cur.execute(
                """
                INSERT INTO CurrentCount (CountTrueValue) VALUES (?)
                """,
                (n,),
            )
        else:
            cur.execute(
                """
                UPDATE CurrentCount SET CountTrueValue = ?
                """,
                (n,),
            )

        if log:
            await ctx.channel.send("I have set the count to {}".format(n))


def compute_correct_fizzbuzz(n):
    if n % 20 == 0 and n % 30 == 0:
        return "fizzbuzz"
    if n % 20 == 0:
        return "fizz"
    if n % 30 == 0:
        return "buzz"
    return str(n)


if __name__ == "__main__":
    with open("secrets/client_login_info.json") as f:
        json_data = json.load(f)
    client.run(json_data.get("clientSecret"))