import discord
import time

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
        last_sweep = time.gmtime(int(cnt.strip()))
        print(f'Last sweep for linked videos: {time.asctime(last_sweep)}')

    await sweep()

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
                channels.append(channel)
    else:
        #Use all channels in guild
        channels = [text_chan.id for text_chan in await server_obj.fetch_channels()]
    
    print(f"Server: {server_obj}\nChannels to scan:{channels}")
    return channels


async def sweep():
    global config

    #sweep in each server (converted to int ID)
    for server in [int(s) for s in config['IDS']['Server'].split(',')]:
        
        channels = await get_channels(server)

        #TODO: scan channel history up to last sweep point

        

def main(useConfig=None):
    global config
    config = useConfig

    if not config:
        #Import config data from config.ini
        from configparser import ConfigParser
        config = ConfigParser()
        config.read("config.ini")

    client.run(config['SECRET']['Token'])