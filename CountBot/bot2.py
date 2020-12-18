import imgkit
import json
import random
from discord.ext.commands import Bot, Context
from discord.ext import commands
import discord
import sqlite3
from discord import NoMoreItems
from tabulate import tabulate
import math
import cv2
import numpy as np
from dateutil.parser import parse
from datetime import datetime

client = commands.Bot(description="Count Bot", command_prefix="!")
print("running")


@client.event
async def on_message(message):
    if message.content.startswith("!errors"):
        args = extract_args(message.content)
        user_name = ""
        if len(args) >= 1:
            user_name = args[0]

        file_name = get_errors(user_name=user_name)
        file = discord.File(file_name)
        await message.channel.send(file=file)

    if message.content.startswith("!counts"):
        args = extract_args(message.content)
        user_name = ""
        if len(args) >= 1:
            user_name = args[0]

        file_name = get_counts(user_name=user_name)
        file = discord.File(file_name)
        await message.channel.send(file=file)
    if message.content.startswith("!counters"):
        file_name = get_counters()
        file = discord.File(file_name)
        await message.channel.send(file=file)
    if message.content.startswith("!time"):
        args = extract_args(message.content)
        if len(args) >= 1:
            user_name = args[0]
            await message.channel.send(time_left(user_name=user_name))
        else:
            await message.channel.send("This command requires a user_name!")
    if message.content.startswith("!ranks"):
        file_name = ranks()
        file = discord.File(file_name)
        await message.channel.send(file=file)


def time_left(*, user_name=""):
    rows = get_errors_from_db(user_name)
    if len(rows) == 0:
        return "No errors found for {}.".format(user_name)
    else:
        now = datetime.utcnow()
        then = parse(rows[0][3])
        time_passed = now - then
        return (
            "{} days, {} hours, {} minutes have passed since {}'s last error.".format(
                time_passed.days,
                time_passed.seconds // 3600,
                (time_passed.seconds // 60) % 60,
                user_name,
            )
        )


def get_counts(*, user_name=""):
    with sqlite3.connect("my_database.db") as conn:
        cur = conn.cursor()

        if user_name == "":
            cur.execute(
                """SELECT Users.Name, Count.SentMessage, Count.Date
                                            FROM Counts as Count
                                            INNER JOIN Counters AS Users
                                                ON Users.ID = Count.UserID
                                            ORDER BY Count.Date DESC
                                            LIMIT 10"""
            )
        else:
            cur.execute(
                """SELECT Users.Name, Count.SentMessage, Count.Date
                                            FROM Counts as Count
                                            INNER JOIN Counters AS Users
                                                ON Users.ID = Count.UserID
                                            WHERE Users.Name = ?
                                            ORDER BY Count.Date DESC
                                            LIMIT 10""",
                (user_name,),
            )

        rows = cur.fetchall()
        to_print = tabulate(
            rows,
            headers=["Counter", "Message", "Date"],
            tablefmt="html",
            numalign="center",
        )

        image_path = "counts.png"
        imgkit.from_string(table_style + to_print, image_path)
        crop_image(image_path)

        return image_path


def get_counters():
    with sqlite3.connect("my_database.db") as conn:
        cur = conn.cursor()


        cur.execute(
            """
                   SELECT Users.Name,
                     (SELECT COUNT(*) FROM Counts WHERE UserID = Users.ID) AS GoodCounts,
                     (SELECT COUNT(*) FROM Errors WHERE UserID = Users.ID) AS BadCounts,
                     (SELECT COUNT(*) FROM Counts WHERE UserID = Users.ID
                        AND Date BETWEEN datetime('now', '-6 days') AND datetime('now', 'localtime')
                     ) AS GoodCountsPastTwoWeeks,
                     (SELECT COUNT(*) FROM Errors WHERE UserID = Users.ID
                        AND Date BETWEEN datetime('now', '-6 days') AND datetime('now', 'localtime')
                     ) AS BadCountsPastTwoWeeks
                    FROM Counters AS Users
                    ORDER BY GoodCounts DESC
            """
        )

        ranks = get_ranks()

        rows = cur.fetchall()
        rated_scores = []
        for counter in rows:
            rating, forgiven = compute_rating_score(counter[1], counter[2], counter[3], counter[4])
            rank = get_rank_from_rating(rating, ranks)
            rated_scores.append((counter[0], rank, rating, counter[1], counter[2], counter[3], counter[4], forgiven))

        rated_scores.sort(key=lambda x: float(x[2]))
        rated_scores.reverse()

        to_print = tabulate(
            rated_scores,
            headers=["Counter", "Rank", "ELO", "Good Counts", "Bad Counts", "Good Counts Week", "Bad Counts Week", "Bad Counts Forgiven"],
            tablefmt="html",
            numalign="center",
        )

        image_path = "counts.png"
        imgkit.from_string(table_style + to_print, image_path)
        crop_image(image_path)

        return image_path


def get_errors_from_db(user_name):
    with sqlite3.connect("my_database.db") as conn:
        cur = conn.cursor()

        if user_name == "":
            cur.execute(
                """SELECT Users.Name, Error.SentMessage, Error.ExpectedMessage, Error.Date
                                            FROM Errors as Error
                                            INNER JOIN Counters AS Users
                                                ON Users.ID = Error.UserID
                                            ORDER BY Error.Date DESC
                                            LIMIT 10"""
            )
        else:
            cur.execute(
                """SELECT Users.Name, Error.SentMessage, Error.ExpectedMessage, Error.Date
                                            FROM Errors as Error
                                            INNER JOIN Counters AS Users
                                                ON Users.ID = Error.UserID
                                            WHERE Users.Name = ?
                                            ORDER BY Error.Date DESC
                                            LIMIT 10""",
                (user_name,),
            )

        rows = cur.fetchall()
        return rows


def get_rank_from_rating(rating, ranks):
    to_return = ""
    for rank in ranks:
        if int(rating) >= rank[1]:
            to_return = rank[0]
        else:
            break
    return to_return


def get_ranks():
    with open("secrets/ranks.json") as ranks:
        ranks = json.load(ranks)
    rank_array = ranks["ranks"]
    to_return = []
    for rank in rank_array:
        to_return.append((rank["rank_name"], rank["elo_threshold"]))
    return to_return


def ranks():
    to_display = get_ranks()

    to_display.reverse()
    to_print = tabulate(
        to_display,
        headers=["Rank", "ELO Threshold (Must be above)"],
        tablefmt="html",
        numalign="center",
    )

    image_path = "ranks.png"
    imgkit.from_string(table_style + to_print, image_path)
    crop_image(image_path)

    return image_path


def get_errors(*, user_name=""):
    rows = get_errors_from_db(user_name)
    to_print = tabulate(
        rows,
        headers=["Counter", "Sent Message", "Expected Message", "Error Date"],
        tablefmt="html",
        numalign="center",
    )

    image_path = "errors.png"
    imgkit.from_string(table_style + to_print, image_path)
    crop_image(image_path)

    return image_path


def crop_image(file_path):
    img = cv2.imread(file_path)

    ## (1) Convert to gray, and threshold
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    th, threshed = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

    ## (2) Morph-op to remove noise
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    morphed = cv2.morphologyEx(threshed, cv2.MORPH_CLOSE, kernel)

    ## (3) Find the max-area contour
    cnts = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    cnt = sorted(cnts, key=cv2.contourArea)[-1]

    ## (4) Crop and save it
    x, y, w, h = cv2.boundingRect(cnt)
    dst = img[y : y + h, x : x + w]
    cv2.imwrite(file_path, dst)


@client.event
async def on_ready():
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


def extract_args(message):
    split = message.split(" ")
    if len(split) > 1:
        return split[1:]
    return []


def compute_rating_score(good_counts, bad_counts, week_good, week_bad):
    adjusted_bad = bad_counts
    if week_good > 150:
        adjusted_bad = week_bad

    rating = ((good_counts / 4) / (1 + (adjusted_bad / 10))) * 53.4283
    if rating <= 0:
        rating = 1

    rating = math.ceil(math.log(rating, 2.5) * 1000)
    return str(rating), bad_counts - adjusted_bad


table_style = """
<style>
  table {
    font-family: "Whitney", Helvetica, sans-serif;
    border-collapse: collapse;
    font-size: 20px;
  }
  table td,
  table th {
    border: 1px solid #ddd;
    padding: 8px;
  }

  table tr:nth-child(even) {
    background-color: #23272a;
  }

  table tr:nth-child(odd) {
    background-color: #2c2f33;
  }

  table tr {
    color: white;
  }

  table th {
    padding-top: 12px;
    padding-bottom: 12px;
    text-align: center;
    background-color: #7289da;
    color: white;
  }
</style>
"""

# imgkit.from_string(style + to_print, "out.jpg")

if __name__ == "__main__":
    with open("secrets/client_login_info.json") as f:
        json_data = json.load(f)
    client.run(json_data.get("statSecret"))