import discord
from datetime import datetime
import re, os, requests

intents = discord.Intents.all()
client = discord.Client(intents=intents)

download_folder = os.path.abspath("./downloads")

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

#Try to log the last sweeped time before quitting application
@client.event
async def on_disconnect():
    print(f"Logging {datetime.utcnow().isoformat()} as last sweep")
    print("Logging out....")
    with open("log.txt", 'w') as f:
        f.write(str(int(datetime.utcnow().timestamp())))

#Handle messages which were sent while bot is active
@client.event
async def on_message(m):
    if m.author == client.user or m.content == None:
        return

    await check_msg(m)

#Download a video from the discord cdn link, return filepath
async def download(link:str):
    fname = link.split("/")[-1]

    fpath = os.path.join(download_folder, fname)

    #file with this name has already been downloaded; avoid overwrites
    i = 1
    if os.path.exists(fpath):
        newpath = fpath[:-4] + f"({i})" + fpath[-4:]
        while os.path.exists(newpath):
            i+=1
            newpath = fpath[:-4] + f"({i})" + fpath[-4:]
        fpath = newpath 

    print(f"Downloading {fname}")
    resp = requests.get(link)
    with open(fpath, 'wb') as f:
        f.write(resp.content)
    
    return fpath


async def check_msg(m):
    global config

    link_reg = re.compile(r'https://(cdn|media).discordapp.com/attachments/[a-zA-Z0-9/.\-_]*((.mp4)|(.mov)|(.webm))')
    res = link_reg.search(m.content)
    
    if not res:
        return None

    vidpath = await download(res.group())

    sent = None
    if config['OPTIONS']['PostAsReply']:
        #Reply to message
        sent = await m.reply(file=discord.File(vidpath))
    else:
        #Send in channel
        sent = await m.channel.send(file=discord.File(vidpath))
    
    if sent:
        os.remove(vidpath)
    else:
        print(f"We never sent that vidpath {vidpath}! Idk man!")


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

    print(f"Sweeping after {last_sweep.isoformat()}")

    started_sweep = datetime.utcnow()

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
    
    #update the last channel history sweep
    last_sweep = started_sweep

    print("Closing connection...")
    await client.close()


def main(useConfig=None):
    global config
    config = useConfig

    if not config:
        #Import config data from config.ini
        from configparser import ConfigParser
        config = ConfigParser()
        config.read("config.ini")

    client.run(config['SECRET']['Token'])