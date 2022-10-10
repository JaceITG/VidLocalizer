import discord
from datetime import datetime
import re

intents = discord.Intents.all()
client = discord.Client(intents=intents)

last_sweep = 0
config = None


### On bot startup/ready ###
@client.event
async def on_ready():
    global last_sweep

    print('We have logged in as {0.user}'.format(client))

    with open("log.txt", 'r') as f:
        cnt = f.read()
        last_sweep = datetime.fromtimestamp(int(cnt.strip()))
        print(f'Last sweep for linked videos: {last_sweep}')

    await sweep()

#TEMP: investigate what linked video messages look like
@client.event
async def on_message(m):
    print(m)
    print(m.content)
    print(len(m.attachments))
    if len(m.attachments) > 0:
        print(m.attachments[0])

    print("Regex ~~~~~~~~~~~~~~~~")
    await check_msg(m)

async def check_msg(m):
    link_reg = re.compile(r'https://cdn.discordapp.com/attachments/[a-zA-Z0-9/.\-]*((.mp4)|(.mov)|(.webm))')
    res = link_reg.search(m.content)
    
    if not res:
        return None

    link = res.group()





#return list of applicable channel objects in server
async def get_channels(server):
    global config

    try:
        server_obj = await client.fetch_guild(server)
    except discord.Forbidden:
        print(f"Error: bot does not have access to server ID {server}")
        return []
    
    channels = []
    
    #Generate list of channels to scan
    if config['IDS']['Channel']:
        #Use list of select channels
        for channel in [int(c) for c in config['IDS']['Channel'].split(',')]:
            if channel in [text_chan.id for text_chan in await server_obj.fetch_channels()]:
                if channel.type == "text":
                    channels.append(channel)
    else:
        #Use all channels in guild
        channels = [text_chan for text_chan in await server_obj.fetch_channels() if text_chan.type == discord.ChannelType.text]
    
    print(f"Server: {server_obj}\nChannels to scan:{[c.name for c in channels]}")
    return channels


async def sweep():
    global config, last_sweep

    #sweep in each server (converted to int ID)
    for server in [int(s) for s in config['IDS']['Server'].split(',')]:
        
        #list of channel objects for this server ID
        channels = await get_channels(server)

        server_obj = await client.fetch_guild(server)

        #go through retreived channels for this server
        for c in channels:
            
            #scan this channel's history, starting at last sweep
            
            async for m in c.history(limit=None, after=last_sweep):
                await check_msg(m)


        

def main(useConfig=None):
    global config
    config = useConfig

    if not config:
        #Import config data from config.ini
        from configparser import ConfigParser
        config = ConfigParser()
        config.read("config.ini")

    client.run(config['SECRET']['Token'])