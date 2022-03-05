import discord
from discord.ext import commands
import bot_functions/music_functions

class Commands(commands.Cogs):
  
  def __init__(self, client):
    self.client = client

  @commands.command(
    brief= "-init",
    description="For first time initializing only",
  )
  async def init(self, ctx):
    print("Initialized")
  
  # ------------------------------------------
  # Play commands
  # ------------------------------------------

  @commands.command(
    brief="-p <query/link> || -play <query/link>",
    description="Play a song from youtube", 
    aliases=['p'],
  )
  async def play(self, ctx):
    print("Play")


  @commands.command(
    brief="-q <query/link> || -queue <query/link>",
    description="Add a song to the end of the queue",
    aliases=['q'],
  )
  async def queue(self, ctx):
    print("Queue")


  @commands.command(
    brief="-qi <index> <query/link> || -queueInsert <index> <query/link>",
    description="Insert a song at a specific index of the queue",
    aliases=['qi'],
  )
  async def queueInsert(self, ctx):
    print("Queue insert")


  @commands.command(
    brief="-n || -next",
    description="Play the next song in queue, if any",
    aliases=['n'],
  )
  async def next(self, ctx):
    print("Next")


  @commands.command(
    brief="-j <index> || -jump <index>",
    description="Play the song at the specified index", 
    aliases=['j'],
  )
  async def jump(self, ctx):
    print("Jump")


  @commands.command(
    brief="-pause",
    description="Pauses the current song playing if any",
  )
  async def pause(self, ctx):
    print("Pause")


  @commands.command(
    brief="-resume",
    description="Resumes the current song paused if any",
  )
  async def resume(self, ctx):
    print("Resume")


  @commands.command(
    brief="-stop || -quit",
    description="Stop the music bot and clear song queue",
    aliases=['quit']
  )
  async def stop(self, ctx):
    print("Stop")

  # ------------------------------------------
  # Queue commands
  # ------------------------------------------
  
  @commands.command(
    brief="-c || -clear",
    description="Clear the song queue. No undos!",
    aliases=['c'],
  )
  async def clear(self, ctx):
    print("Clear")


  @commands.command(
    brief="-i <old> <new> || -insert <old> <new>",
    description="Insert song at old index at the new index. Insert at front if new not specified",
    aliases=['i'],
  )
  async def insert(self, ctx, *args):
    print("Insert")

  
  @commands.command(
    brief="-r <index> || -remove <index>",
    description="Removes the song at specified index",
    aliases=['r'],
  )
  async def remove(self, ctx, index):
    print("Remove")

  # ------------------------------------------
  # Config commands
  # ------------------------------------------

  # To be added



  # ------------------------------------------
  # Display commands
  # ------------------------------------------

  # To be added



  # ------------------------------------------
  # Developer commands
  # ------------------------------------------

  