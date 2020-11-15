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


@client.event
async def on_message(message):
    if message.channel.id == ranked_counting_channel_id:
        # THIS IS NOT A DRILL, WE ARE COUNTING
        pass

    if message.author.id == 82969926125490176 and message.content == "!generate_db":
        await message.channel.send(
            "Re-generating counting database from channel {}".format(
                ranked_counting_channel_id
            )
        )
        await generate_db(message)
    if message.content.startswith("!show_errors"):
        args = extract_args(message.content)
        user_name = ""
        if len(args) >= 1:
            user_name = args[0]
        print(user_name)
        await message.channel.send(get_errors(user_name=user_name))
    if message.content.startswith("!show_counters"):
        await message.channel.send(get_counters())


def extract_args(message):
    split = message.split(" ")
    if len(split) > 1:
        return split[1:]
    return []


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


def get_errors(*, user_name=""):
    with sqlite3.connect("my_database.db") as conn:
        cur = conn.cursor()

        if user_name == "":
            cur.execute(
                """SELECT Users.Name, Error.ExpectedMessage, Error.Date
                                            FROM Errors as Error
                                            INNER JOIN Counters AS Users
                                                ON Users.ID = Error.UserID
                                            LIMIT 10"""
            )
        else:
            cur.execute(
                """SELECT Users.Name, Error.ExpectedMessage, Error.Date
                                            FROM Errors as Error
                                            INNER JOIN Counters AS Users
                                                ON Users.ID = Error.UserID
                                            WHERE Users.Name = ? LIMIT 10""",
                (user_name,),
            )

        rows = cur.fetchall()
        to_print = tabulate(rows, ["Counter", "Expected Message", "Error Date"])

        return f"```python\n{to_print}\n```"


def get_counters():
    with sqlite3.connect("my_database.db") as conn:
        cur = conn.cursor()

        cur.execute(
            """SELECT Users.Name,
                     (SELECT COUNT(*) FROM Counts WHERE UserID = Users.ID) AS GoodCounts,
                     (SELECT COUNT(*) FROM Errors WHERE UserID = Users.ID) AS BadCounts
                    FROM Counters AS Users
                    ORDER BY GoodCounts DESC
            """
        )

        rows = cur.fetchall()
        rated_scores = []
        for counter in rows:
            rating = compute_rating_score(counter[1], counter[2])
            rated_scores.append((counter[0], rating, counter[1], counter[2]))

        rated_scores.sort(key=lambda x: float(x[1]))
        rated_scores.reverse()

        to_print = tabulate(
            rated_scores,
            headers=["Counter", "ELO", "Good Counts", "Bad Counts"],
            tablefmt="psql",
            numalign="right",
        )

        return f"```python\n{to_print}\n```"


def compute_rating_score(good_counts, bad_counts):
    rating = (good_counts - (bad_counts * 20)) * 53.4283

    if rating < 0:
        rating = 0
    return str(rating)


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