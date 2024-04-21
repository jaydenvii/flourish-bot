import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import io
import csv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("online")

#testing command
@bot.command()
async def ping(ctx):
    await ctx.send("pong")
    await ctx.send("\'\'\'hello\'\'\'")

#counts messages sent in a server by person
async def countMessages(ctx):
    counts = {}
    async for message in ctx.channel.history(limit=None):
        author = message.author.display_name
        counts[author] = counts.get(author, 0) + 1

    return counts

#sends the dict from countMessages() as a csv
@bot.command()
async def userMessages(ctx):
    counts = await countMessages(ctx)

    csvData = io.StringIO()
    csvWriter = csv.writer(csvData)
    csvWriter.writerow(["User", "Count"])
    for user, count in counts.items():
        csvWriter.writerow([user, count])

    csv_content = csvData.getvalue()

    await ctx.send(file=discord.File(io.BytesIO(csv_content.encode()), filename="counts.csv"))

bot.run(TOKEN)