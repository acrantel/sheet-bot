import discord
from discord.utils import get

import random
import pickle
import os.path
import json

import time

client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author.id in [583806500443652102, 723063395280224257]:
        split_msg = message.content.split(' ', 2)
        if len(split_msg) >= 3 and split_msg[0].lower() == 'spam':
            num = int(split_msg[1])
            for x in range(min(num, 75 if message.author.id == 583806500443652102 else 5)):
                time.sleep(.4)
                await respond(message, split_msg[2])

async def respond(message, response):
    await message.channel.send(response)

client.run(open('discord_token.txt').readline().strip())


