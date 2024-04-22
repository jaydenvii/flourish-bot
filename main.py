import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
import io
import csv
from datetime import datetime

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix=",,", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("online")

#testing command
@bot.command()
async def ping(ctx):
    await ctx.send("pong")

#counts messages sent in a channel by person
async def countChannelMessages(channel):
    counts = {}

    # counts all messages
    async for message in channel.history(limit=None):
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

    # create sum array
    for countsPerUser in counts.values():
        summedCounts = list(countsPerUser.values())
        
        for i in range(1, len(summedCounts)):
            summedCounts[i] += summedCounts[i-1]

        for countsPerMonth in countsPerUser.keys():
            countsPerUser[countsPerMonth] = summedCounts.pop(0)

    return counts

#counts messages sent in all channels by person
@bot.command() #remove command
async def countAllMessages(ctx):
    allCounts = {}

    # repeatedly calls countChannelMessages for every channel
    for channel in ctx.guild.channels:
        channelCounts = await countChannelMessages(discord.utils.get(ctx.guild.channels, id=channel.id))
        for author, countsPerUser in channelCounts.items():
            if author not in allCounts:
                    allCounts[author] = {}

            for month, countsPerMonth in countsPerUser.items():
                if month not in allCounts[author]:
                    allCounts[author][month] = countsPerMonth
                else:
                    allCounts[author][month] += countsPerMonth

    return allCounts

#sends the dict from countMessages() as a csv
async def sendCSV(ctx, counts):
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

    # add each row
    for user, count in counts.items():
        row = [user] + [count.get(month, 0) for month in header[1:]]
        csvWriter.writerow(row)

    csvContent = csvData.getvalue()

    await ctx.send(file=discord.File(io.BytesIO(csvContent.encode()), filename="counts.csv"))

@bot.command()
async def currentChannel(ctx):
    counts = await countChannelMessages(ctx.channel)

    await sendCSV(ctx, counts)

@bot.command()
async def allChannels(ctx):
    allCounts = await countAllMessages(ctx.channel)

    await sendCSV(ctx, allCounts)

bot.run(TOKEN)