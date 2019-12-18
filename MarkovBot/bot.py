import json
import random
from discord.ext.commands import Bot, Context
from discord.ext import commands
from discord import NoMoreItems

client = commands.Bot(description="Markov Bot", command_prefix="!")


@client.command()
async def generate_message(ctx: Context, username: str, length: int):
    await ctx.send(f"Generating message...")

    user_id = int("".join(i for i in username if i.isdigit()))
    messages = ctx.channel.history(limit=None).filter(
        lambda message: message.author.id == user_id
    )

    user_words = []
    num_messages = 0
    while True:
        try:
            message = await messages.next()
            content = message.content
            if not content.startswith("!"):
                num_messages += 1
                for w in get_processed_string(content).split(" "):
                    if len(w) < 12:
                        user_words.append(w)
        except NoMoreItems:
            break
        except:
            continue

    await ctx.send(
        f"Processed {num_messages} messages containing {len(user_words)} words..."
    )

    user_message, _ = get_message(user_words, length)
    await ctx.send(f"{username}-bot Says: {user_message}")


# ----- ----- ----- ----- ----- ----- ----- ----- ----- #


def get_processed_string(string):
    toRemove = [
        "\n",
        ".",
        ",",
        "!",
        "?",
        "[",
        "]",
        "*",
        ";",
        ":",
        "(",
        ")",
        "^",
        '"',
        "'",
    ]
    toReturn = string
    for remove in toRemove:
        toReturn = toReturn.replace(remove, "")

    return toReturn.lower()


# ----- ----- ----- ----- ----- ----- ----- ----- ----- #


def get_message(comments, count):
    chain = {}

    index = 1
    for word in comments[index:]:
        key = comments[index - 1]
        if key in chain:
            chain[key].append(word)
        else:
            chain[key] = [word]

        index += 1

    word1 = random.choice(list(chain.keys()))
    message = word1.capitalize()

    while len(message.split(" ")) < count:
        if word1 != "":
            try:
                fail = True
                for i in range(100):
                    try:
                        word2 = random.choice(chain[word1])
                        fail = False
                        break
                    except:
                        continue
                if fail:
                    raise Exception()
            except:
                break

            word1 = word2
            message += " " + word2
        else:
            word1 = random.choice(chain[word1])

    return message, chain


# ----- ----- ----- ----- ----- ----- ----- ----- ----- #

if __name__ == "__main__":
    with open("client_login_info.json") as f:
        json_data = json.load(f)
    client.run(json_data.get("clientSecret"))
