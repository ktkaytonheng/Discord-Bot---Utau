import discord
from discord.ext import commands
import youtube_dl
import urllib.parse, urllib.request, re
import asyncio
import random

class music(commands.Cog):
  # DEFAULT CONFIGURATIONS ==========================================
  YDL_OPTIONS = {'format': "bestaudio"}

  # LOCAL DATABASE ==================================================
  songQueue = {}
  songHistory = {}
  currentSong = {}

  lastSentEmbed = {}
  songTimerEmbed = {}
  
  songTimer = {}
  exitTimer = {}
  lockPlay = {}
  onSkip = {}
  onRepeat = {}
  onStop = {}
  onPause = {}
  onShuffle = {}

  def __init__(self, client):
    self.client = client

  # ============================== COMMANDS =================================
  
  # --------------
  # Main functions
  # --------------
  @commands.command(
    brief="-init",
    description="Initialize Utau in the current guild.",
  )
  async def init(self, ctx):
    guild = ctx.guild.id
    if guild in self.songQueue:
      await ctx.send("I'm already initialized here!")
    else:
      print("Initialized by " + ctx.guild.name)
      await ctx.send("Initializing...")
      self.songQueue[guild] = []
      self.songHistory[guild] = []
      self.currentSong[guild] = None
      self.lastSentEmbed[guild] = None
      self.onSkip[guild] = False
      self.onRepeat[guild] = False
      self.onStop[guild] = False
      self.onPause[guild] = False
      self.onShuffle[guild] = False
      self.lockPlay[guild] = False
      self.exitTimer[guild] = 0
      self.songTimer[guild] = 0
      self.songTimerEmbed[guild] = None
      await asyncio.sleep(1)
      await ctx.send("Stalking everyone's profiles and browsing history...")
      await asyncio.sleep(1)
      await ctx.send("Warming up my vocals...")
      await asyncio.sleep(1)
      await ctx.send("I'm ready to go! :yum:")
      await ctx.send(embed=self.newFeature)

  @commands.command(
    brief="-disconnect",
    description="Disconnect the bot from the voice chat")
  async def disconnect(self, ctx):
    if not await self.checkInit(ctx):
      return
    await ctx.voice_client.disconnect()
    self.currentSong[ctx.guild.id] = None
  
  @commands.command(
    brief="-help",
    description="Display the list of available commands")
  async def help(self, ctx):
    embed = discord.Embed(
      title="Hey everyone, here are the commands that I understand!",
      colour=0x87CEEB
    )
    embed.set_author(
      name="Utau", 
      icon_url="https://cdn-icons-png.flaticon.com/512/651/651799.png"
    )
    command_list = list(self.client.commands)
    command_list.sort(key=lambda x: x.brief)
    for command in command_list:
      if command != 'checkBooleans':
        embed.add_field(name=command.brief, value=command.description, inline=False)
    await ctx.send(embed=embed)

  # --------------
  # Play commands
  # --------------
  @commands.command(
    brief="-p <query/link> || -play <query/link>",
    description="Play a song from youtube", 
    aliases=['p'])
  async def play(self, ctx, *args):
    if not await self.checkInit(ctx):
      return
    if await self.checkLockPlay(ctx):
      return
    if len(args) == 0:
      if len(self.songQueue[ctx.guild.id]) != 0:
        await self.next(ctx)
      else:
        await ctx.send("There's nothing to play :<")
      return

    await self.join(ctx)
    if ctx.author.voice is None:
      return

    url = await self.ytSearch(args)
    with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
      try:
        info = ydl.extract_info(url, download=False)
      except:
        await ctx.send("Your link/query giving me some errors... ")
        await ctx.send("Try another instead?")
        return
    self.currentSong[ctx.guild.id] = info
    if ctx.voice_client.is_playing():
      self.onSkip[ctx.guild.id] = True
      ctx.voice_client.stop()
    await self.playSong(ctx, info)

  @commands.command(
    brief="-q <query/link> || -queue <query/link>",
    description="Add a song to the end of the queue",
    aliases=['q'])
  async def queue(self, ctx, *args):
    if not await self.checkInit(ctx):
      return
    if len(args) == 0:
      await ctx.send("Please specify at least a name or website :/")
    url = await self.ytSearch(args)
    with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
      try:
        info = ydl.extract_info(url, download=False)
      except:
        await ctx.send("That query or link gives me a video that's restricted...")
        await ctx.send("Perhaps you can try another?")
        return
    if ctx.voice_client is None:
      await self.join(ctx)
    if ctx.voice_client.is_playing() is False and not self.onPause[ctx.guild.id]:
      self.currentSong[ctx.guild.id] = info
      await self.playSong(ctx, self.currentSong[ctx.guild.id])
    else:
      embed = discord.Embed(
        title="Added to song queue",
        description=info['title']
      )
      await ctx.send(embed=embed)
      self.songQueue[ctx.guild.id].append(info)

  @commands.command(
    brief="-qi <index> <query/link> || -queueInsert <index> <query/link>",
    description="Insert a song at a specific index of the queue",
    aliases=['qi'])
  async def queueInsert(self, ctx, *args):
    if not await self.checkInit(ctx):
      return
    if len(args) == 0:
      await ctx.send("You gotta give me something other than the command :/")
    elif not args[0].isdigit():
      await ctx.send("First argument must be a digit.")
    else:
      if len(args) == 1:
        await ctx.send("Please specify at least a name or website :/")
      index = int(args[0])
      url = await self.ytSearch(args[1:])
      with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
        try:
          info = ydl.extract_info(url, download=False)
        except:
          await ctx.send("That query or link gives me a video that's restricted...")
          await ctx.send("Perhaps you can try another?")
          return
      if ctx.voice_client is None:
        await self.join(ctx)
      if ctx.voice_client.is_playing() is False:
        self.currentSong[ctx.guild.id] = info
        await self.playSong(ctx, self.currentSong[ctx.guild.id])
      else:
        embed = discord.Embed(
          title="Added song to queue at index {}".format(min(len(self.songQueue[ctx.guild.id]), index)),
          description=info['title']
        )
        await ctx.send(embed=embed)
        self.songQueue[ctx.guild.id].insert(index-1, info)

  @commands.command(
    brief="-n || -next",
    description="Play the next song in queue, if any",
    aliases=['n'])
  async def next(self, ctx):
    if not await self.checkInit(ctx):
      return
    if not await self.checkInVC(ctx):
      return
    if self.onShuffle[ctx.guild.id]:
      index = str(random.randint(1, len(self.songQueue[ctx.guild.id])))
    else:
      index = '1'
    await self.skip(ctx, index)

  @commands.command(
    brief="-s <index> || -skip <index>",
    description="Play the song at the specified index", 
    aliases=['s'])
  async def skip(self, ctx, index):
    if not await self.checkInit(ctx):
      return
    if len(self.songQueue[ctx.guild.id]) == 0:
      await ctx.send("No songs in queue currently.")
    elif index is None:
      await ctx.send("You gotta specify an index to skip to xD")
    elif not index.isdigit():
      await ctx.send("Please input a number")
    elif int(index)-1 < 0 or int(index)-1 >= len(self.songQueue[ctx.guild.id]):
      await ctx.send("Song index does not exist in queue.")
    else:
      self.currentSong[ctx.guild.id] = self.songQueue[ctx.guild.id].pop(int(index)-1)
      if ctx.voice_client.is_playing():
        self.onSkip[ctx.guild.id] = True
      ctx.voice_client.stop()
      await self.playSong(ctx, self.currentSong[ctx.guild.id])

  @commands.command(
    brief="-pause",
    description="Pauses the current song playing if any")
  async def pause(self, ctx):
    if not await self.checkInit(ctx):
      return
    if await self.checkInVC(ctx):
      if not ctx.voice_client.is_playing():
        await ctx.send("No song currently playing.")
      else:
        ctx.voice_client.pause()
        self.onPause[ctx.guild.id] = True
        await ctx.send("Music paused!")

  @commands.command(
    brief="-resume",
    description="Resumes the current paused song if any")
  async def resume(self, ctx):
    if not await self.checkInit(ctx):
      return
    if await self.checkInVC(ctx):
      if self.currentSong != None:
        ctx.voice_client.resume()
        self.onPause[ctx.guild.id] = False
        await ctx.send("Music resumed!")
      else:
        await ctx.send("Are you sure there is a song paused?")

  @commands.command(
    brief="-stop || -quit",
    description="Stop the music bot and clear song queue",
    aliases=['quit']
  )
  async def stop(self, ctx):
    if not await self.checkInit(ctx):
      return
    if await self.checkInVC(ctx):
      self.onStop[ctx.guild.id] = True
      ctx.voice_client.stop()

  # --------------
  # Queue commands
  # --------------

  @commands.command(
    brief="-c || -clear",
    description="Clear the song queue. No undos!",
    aliases=['c']
  )
  async def clear(self, ctx):
    if not await self.checkInit(ctx):
      return
    self.songQueue[ctx.guild.id].clear()
    await ctx.send("Song queue cleared!")

  @commands.command(
    brief="-i <old> <new> || -insert <old> <new>",
    description="Insert song at old index at the new index. Insert at front if new not specified",
    aliases=['i']
  )
  async def insert(self, ctx, *args):
    if not await self.checkInit(ctx):
      return
    if len(args) == 0:
      await ctx.send("Please specify an index to push to front")
      return
    elif len(args) == 1:
      newIndex = 0
    else:
      newIndex = int(args[1]) - 1
    oldIndex = int(args[0]) - 1
    song = self.songQueue[ctx.guild.id].pop(oldIndex)
    self.songQueue[ctx.guild.id].insert(newIndex, song)
    await ctx.send("{} inserted at index {}".format(song['title'], str(newIndex+1)))

  @commands.command(
    brief="-r <index> || -remove <index>",
    description="Removes the song at specified index",
    aliases=['r'])
  async def remove(self, ctx, index):
    if not await self.checkInit(ctx):
      return
    index = int(index)-1
    if len(self.songQueue[ctx.guild.id]) == 0:
      await ctx.send("No songs in queue")
    elif index >= len(self.songQueue[ctx.guild.id]):
      await ctx.send("Index given is more than what the queue has")
    else:
      self.songQueue[ctx.guild.id].pop(index)
      await ctx.send("Song removed!")
      await ctx.send("Here's the new list")
      await self.displayQueue(ctx)

  # --------------
  # Toggle config commands
  # --------------

  @commands.command(
    brief="-repeat",
    description="Toggle repeat mode"
  ) 
  async def repeat(self, ctx):
    if not await self.checkInit(ctx):
      return
    
    self.onRepeat[ctx.guild.id] = not self.onRepeat[ctx.guild.id]
    if self.onRepeat[ctx.guild.id]:
      await ctx.send("Song is now on repeat: " + self.currentSong[ctx.guild.id]['title'])
    if not self.onRepeat[ctx.guild.id]:
      await ctx.send("Song is no longer in repeat.")
      await self.displayQueue(ctx)
  
  @commands.command(
    brief="-shuffle",
    description="Toggle shuffle mode"
  )
  async def shuffle(self, ctx):
    if not await self.checkInit(ctx):
      return
    self.onShuffle[ctx.guild.id] = not self.onShuffle[ctx.guild.id]
    if self.onShuffle[ctx.guild.id]:
      await ctx.send("Songs are now played randomly~")
    if not self.onShuffle[ctx.guild.id]:
      await ctx.send("Songs are now played in order~")

  @commands.command(
    brief="-lock",
    description="Lock the -play or -p command",
  )
  async def lock(self, ctx):
    self.lockPlay[ctx.guild.id] = not self.lockPlay[ctx.guild.id]
    if self.lockPlay[ctx.guild.id]:
      await ctx.send("The play command is now locked ^^")
    else:
      await ctx.send("The play command is now unlocked ^^")

  # --------------
  # Display commands
  # --------------

  @commands.command(
    brief="-dq || -displayQueue",
    description="Displays the current queue",
    aliases=['dq'])
  async def displayQueue(self, ctx):
    if not await self.checkInit(ctx):
      return
    if len(self.songQueue[ctx.guild.id]) == 0:
      embed = discord.Embed(title="No songs in queue") 
    else:
      queueString = ''
      index = 1 
      for song in self.songQueue[ctx.guild.id]:
        queueString += str(index) + ". " + str(song['title']) + "\n"
        index += 1
      embed = discord.Embed(title="Song queue", description=queueString)
    await ctx.send(embed=embed)
  
  @commands.command(
    brief="-ds || -displaySong",
    description="Displays the current song",
    aliases=['ds'])
  async def displaySong(self, ctx):
    if not await self.checkInit(ctx):
      return
    if await self.checkInVC(ctx):
      if self.onPause[ctx.guild.id]:
        embed = discord.Embed(
          title="Currently paused",
          description=self.currentSong[ctx.guild.id]['title'])
      elif not ctx.voice_client.is_playing():
        embed = discord.Embed(
          title="No songs are currently playing"
        )
      else:
        embed = discord.Embed(
          title="Now Playing",
          description=self.currentSong[ctx.guild.id]['title'])
      await ctx.send(embed=embed)    

  @commands.command(
    brief="-dh || -history",
    description="Display the song history, up till last 30",
    aliases=['dh']
  )
  async def history(self, ctx):
    if not await self.checkInit(ctx):
      return
    if len(self.songHistory[ctx.guild.id]) == 0:
      embed = discord.Embed(
        title="History",
        description="No songs in history"
      ) 
    else:
      index = 1
      historyString = ""
      for song in self.songHistory[ctx.guild.id]:
        historyString += str(index) + ". " + str(song['title']) + "\n"
        index += 1
      embed = discord.Embed(
        title="History",
        description=historyString
      )
    await ctx.send(embed=embed)


  @commands.command(
    brief="-config",
    description="Check the current configuration")
  async def config(self, ctx):
    guild = ctx.guild.id
    if len(self.songQueue[guild]) > 0:
      totalSongDuration = 0
      for i in range(len(self.songQueue[guild])):
        totalSongDuration += self.songQueue[guild][i]['duration']
      totalSongDurationStr = await self.getSongDuration(totalSongDuration)
    else:
      totalSongDurationStr = "No song in queue"
    embed = discord.Embed(
      title="Current configurations"
    )
    embed.add_field(name="Play command locked", value=self.lockPlay[guild], inline=False)
    embed.add_field(name="Repeat mode", value=self.onRepeat[guild], inline=False)
    embed.add_field(name="Shuffle mode", value=self.onShuffle[guild], inline=False)
    embed.add_field(name="No. of songs in queue", value=len(self.songQueue[guild]), inline=False)
    embed.add_field(name="Total song duration", value=totalSongDurationStr, inline=False)
    await ctx.send(embed=embed)

  @commands.command(
    brief="-duration",
    description="Check the current song duration and total duration in queue"
  )
  async def duration(self, ctx):
    if not await self.checkInit(ctx):
      return
    guild = ctx.guild.id
    if self.currentSong[guild] is not None:
      songTimerStr = await self.getSongDuration(self.songTimer[guild])
      songDurationStr = await self.getSongDuration(self.currentSong[guild]['duration'])
      embed = discord.Embed(
        title="Current song duration",
        description="{} / {}".format(songTimerStr, songDurationStr)
      )
      self.songTimerEmbed[guild] = await ctx.send(embed=embed)
    else:
      embed = discord.Embed(
        title="No song playing",
      )
      await ctx.send(embed=embed)

  # --------------
  # Developer commands and test functions
  # --------------

  @commands.command(
    brief="-checkBooleans",
    description="Display the values of the boolean variables",
  )
  async def checkBooleans(self, ctx):
    if not await self.checkInit(ctx):
      return
    guild = ctx.guild.id
    message = ""
    message += "onPause" + str(self.onPause[guild]) + "\n"
    message += "onSkip: " + str(self.onSkip[guild]) + "\n"
    message += "onStop: " + str(self.onStop[guild]) + "\n"
    message += "onRepeat: " + str(self.onRepeat[guild]) + "\n"
    message += "onShuffle: " + str(self.onShuffle[guild])
    await ctx.send(message)

  # ================
  # Async functions
  # ================

  async def sendEmbed(self, ctx, embed):
    if self.lastSentEmbed[ctx.guild.id] is None:
      self.lastSentEmbed[ctx.guild.id] = await ctx.send(embed=embed)
    elif self.lastSentEmbed[ctx.guild.id].id != ctx.channel.last_message_id:
      self.lastSentEmbed[ctx.guild.id] = await ctx.send(embed=embed)
    else:
      await self.lastSentEmbed[ctx.guild.id].edit(embed=embed)
    

  async def getSongDuration(self, seconds):
    hours = int(seconds / 3600)
    minutes = int((seconds - hours*3600) / 60)
    seconds = int(seconds - hours*3600 - minutes*60)
    minutesStr = "0" + str(minutes) if (minutes<10) else str(minutes)
    secondsStr = "0" + str(seconds) if (seconds<10) else str(seconds)
    return "{}:{}:{}".format(hours,minutesStr,secondsStr)

  async def join(self, ctx):
    if ctx.author.voice is None:
      await ctx.send("Join a voice channel first.")
      return
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
      print("Connecting to channel")
      await voice_channel.connect()
    elif ctx.voice_client.channel == voice_channel:
      print("Already in same channel")
    else:
      print("Changing channel")
      await ctx.voice_client.move_to(voice_channel)

  async def playSong(self, ctx, info):
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    
    url = info['formats'][0]['url']
    vc = ctx.voice_client

    source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS)
    loop = asyncio.get_event_loop()
    vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(self.after_song(ctx), loop))
    embed = discord.Embed(
      title="Now playing",
      description=self.currentSong[ctx.guild.id]['title'],
    )
    await self.sendEmbed(ctx, embed)
    await self.startSongTimer(ctx)
  
  async def addCurrentSongToHistory(self, ctx):
    if len(self.songHistory[ctx.guild.id]) == 30:
      self.songHistory[ctx.guild.id].pop(0)
    elif len(self.songHistory[ctx.guild.id]) != 0 and self.songHistory[ctx.guild.id][-1] == self.currentSong[ctx.guild.id]:
      return
    self.songHistory[ctx.guild.id].append(self.currentSong[ctx.guild.id])
      
  async def after_song(self, ctx):
    print("Song ended")
    guild = ctx.guild.id
    self.songTimer[guild] = 0
    self.songTimerEmbed[guild] = None
    print("Adding song to history")
    await self.addCurrentSongToHistory(ctx)
    try:
      if self.onStop[guild]:
        print("Stopping")
        await self.clear(ctx)     
        self.currentSong[guild] = None
        self.onStop[guild] = False
        self.onPause[guild] = False
        await ctx.send("See you again~ ^^")
        await self.disconnect(ctx)
      elif self.onSkip[guild]:
        print("Skipping")
        self.onSkip[guild] = False
        self.onRepeat[guild] = False
      elif self.onRepeat[guild]:
        print("Repeating")
        await self.playSong(ctx, self.currentSong[guild])
      elif len(self.songQueue[guild]) > 0:
        print("Next song")
        await self.next(ctx)
      else:
        print("No more songs in queue")
        self.currentSong[guild] = None
        self.onPause[guild] = False
        embed = discord.Embed(
          title="No more songs in queue"
        )
        await self.sendEmbed(ctx, embed)
        await self.startTimerForInactivity(ctx)
    except IndexError :
      pass

  async def ytSearch(self, url):
    if url[0].startswith("https://"):
      return url[0]
    else:
      query = ''
      for word in url:
        query += word + ' '
      print(query)
      query_string = urllib.parse.urlencode({'search_query': query})
      html_content = urllib.request.urlopen('http://www.youtube.com/results?' + query_string)
      search_content = html_content.read().decode()
      search_results = re.findall(r'\/watch\?v=[\w\-]+', search_content)
      print(search_results[:5])
      return 'https://www.youtube.com' + search_results[0]

  async def startTimerForInactivity(self, ctx):
    self.exitTimer[ctx.guild.id] = 0
    embed = discord.Embed(
      title="Timer till bot disconnects",
      description=str(60-self.exitTimer[ctx.guild.id]),
    )
    msg = await ctx.send(embed=embed)
    while True:
      await asyncio.sleep(1)
      self.exitTimer[ctx.guild.id] += 1
      newEmbed = discord.Embed(
        title="Timer till bot disconnects",
        description=str(60-self.exitTimer[ctx.guild.id]),
      )
      await msg.edit(embed=newEmbed)
      if self.exitTimer[ctx.guild.id] == 60:
        await self.disconnect(ctx)
        await msg.delete()
      elif ctx.voice_client.is_playing():
        await msg.delete()
        return
    
  async def startSongTimer(self, ctx):
    guild = ctx.guild.id
    while True:
      if self.songTimerEmbed[guild] is not None:
        songTimerStr = await self.getSongDuration(self.songTimer[guild])
        songDurationStr = await self.getSongDuration(self.currentSong[guild]['duration'])
        embed = discord.Embed(
          title="Current song duration",
          description="{} / {}".format(songTimerStr, songDurationStr)
        )
        await self.songTimerEmbed[guild].edit(embed=embed)
      await asyncio.sleep(1)
      self.songTimer[guild] += 1
      if ctx.voice_client is None:
        return
      if not ctx.voice_client.is_playing():
        return

  async def checkLockPlay(self, ctx):
    if self.lockPlay[ctx.guild.id]:
      await ctx.send("Play command is locked! Use -q or -queue instead")
      return True
    else:
      return False
  
  async def checkInVC(self, ctx):
    if ctx.voice_client is None:
      await ctx.send("B-but… I’m not in any channels! 👉🏼👈🏼")
      return False
    else:
      return True

  async def checkInit(self, ctx):
    if ctx.guild.id in self.songQueue:
      return True
    else:
      await ctx.send("You gotta initialize me with -init first! ")
      return False
  
def setup(client):
  client.add_cog(music(client))