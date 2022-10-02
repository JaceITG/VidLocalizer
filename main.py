import discord
import time

intents = discord.Intents.all()
client = discord.Client(intents=intents)

last_sweep = 0

def main(useConfig=None):
    config = useConfig

    if not config:
        #Import config data from config.ini
        from configparser import ConfigParser
        config = ConfigParser()
        config.read("config.ini")

    client.run(config['SECRET']['Token'])

#On bot startup/ready
@client.event
async def on_ready():
    global last_sweep

    print('We have logged in as {0.user}'.format(client))

    with open("log.txt", 'r') as f:
        cnt = f.read()
        last_sweep = time.gmtime(int(cnt.strip()))
        print(last_sweep)

