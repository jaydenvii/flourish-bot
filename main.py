import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import io
import csv
from datetime import datetime

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("online")

#testing command
@bot.command()
async def ping(ctx):
    await ctx.send("pong")

#counts messages sent in a server by person
async def countMessages(ctx):
    counts = {}

    # counts all messages
    async for message in ctx.channel.history(limit=None):
        author = message.author.display_name
        month = message.created_at.strftime("%B %Y")
        
        if author not in counts:
            counts[author] = {}
        if month not in counts[author]:
            counts[author][month] = 1
        else:
            counts[author][month] += 1

    # sorts months from earliest to latest
    for countsPerUser in counts.values():
        sortedMonths = sorted(countsPerUser.keys(), key=lambda x: datetime.strptime(x, "%B %Y"))
        countsPerUserSorted = {date: countsPerUser[date] for date in sortedMonths}
        countsPerUser.clear()
        countsPerUser.update(countsPerUserSorted)

    return counts

#sends the dict from countMessages() as a csv
@bot.command()
async def messagesCSV(ctx):
    counts = await countMessages(ctx)

    csvData = io.StringIO()
    csvWriter = csv.writer(csvData)

    # find and sort all months in the data (remove duplicates for later)
    allMonths = set()
    for countsPerUser in counts.values():
        allMonths.update(countsPerUser.keys())

    sortedMonths = sorted(allMonths, key=lambda x: datetime.strptime(x, "%B %Y"))

    # header
    header = ["User"] + sortedMonths
    csvWriter.writerow(header)

    for user, count in counts.items():
        row = [user] + [count.get(month, 0) for month in header[1:]]
        csvWriter.writerow(row)

    csvContent = csvData.getvalue()

    await ctx.send(file=discord.File(io.BytesIO(csvContent.encode()), filename="counts.csv"))

bot.run(TOKEN)