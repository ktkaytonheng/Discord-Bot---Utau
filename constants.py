import enum

class BotConstants:
  BOT_NAME: 'Utau'
  ICON_URL: 'https://cdn-icons-png.flaticon.com/512/651/651799.png'
  
class Colours:
  SKYBLUE = 0x87CEEB

class MusicConstants:
  YDL_OPTIONS = {'format': "bestaudio"}
  FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}