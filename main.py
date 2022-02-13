import discord
from discord.ext import commands
import music
from keep_alive import keep_alive

cogs = [music]

client = commands.Bot(command_prefix="-", 
      intents = discord.Intents.all(), 
      help_command=None)

for i in range(len(cogs)):
  cogs[i].setup(client)

print("Starting bot...")

keep_alive()
client.run("OTA5ODM5Mjc5OTAyMDUyMzkz.YZKH3A.wN31rFuyBBqgfF6V9nq7K8gj2I8")