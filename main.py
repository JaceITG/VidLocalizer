import discord

import configparser, time

intents = discord.Intents.all()
client = discord.Client(intents=intents)

#On bot startup/ready
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

    