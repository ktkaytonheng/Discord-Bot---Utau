import discord
from discord.ext import commands

from keep_alive/keep_alive import keep_alive
import bot_functions/music
import bot_functions/chat

import os


bot_token = os.environ['bot_token']

cogs = [music]

client = commands.Bot(command_prefix="-", 
      intents = discord.Intents.all(), 
      help_command=None)

for i in range(len(cogs)):
  cogs[i].setup(client)

print("Starting bot...")

keep_alive()
client.run(bot_token)