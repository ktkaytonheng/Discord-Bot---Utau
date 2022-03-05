import discord
import youtube_dl
import urllib.parse, urllib.request, re
import time
import random
from constants import MusicConstants

class Music:
  
  async def yt_search(self, query):
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

  async def play_song(self, ctx, query):
    url = self.yt_search(query)
    with youtube_dl.YoutubeDL(MusicConstants.YDL_OPTIONS) as ydl:
      try:
        info = ydl.extract_info(url, download=False)
      except:
        await ctx.send("Your link/query giving me some errors... ")
        await ctx.send("Try another instead?")
        return
    if ctx.voice_client.is_playing():
      ctx.voice_client.stop()
    url = info['formats'][0]['url']
    vc = ctx.voice_client

    source = await discord.FFmpegOpusAudio.from_probe(url, **MusicConstants.FFMPEG_OPTIONS)
    loop = asyncio.get_event_loop()
    vc.play(source, after=print("Done"))
