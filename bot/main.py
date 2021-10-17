import discord
from discord.ext import commands, tasks
from discord.voice_client import VoiceClient
import youtube_dl
token = 'ODc1MTA4OTUxODk5OTIyNDQz.YRQuuA.4uVbZV3BbmXmASA5af0o1GPtD_E'
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)





from random import choice

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


client = commands.Bot(command_prefix='?')



@client.event
async def on_ready():
    change_status.start()
    print('Bot is online!')

@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='general')
    await channel.send(f'Welcome {member.mention}!  Ready to jam out? bekijk de `?help` command voor de details!')



@client.command(name='hello', help='Deze commando zegt een random hi message!')
async def hello(ctx):
    responses = ['***Ughh*** Waarom heb je me nou wakker gemaakt?', 'Goedemorgen mensen!', 'Hallo! hoe gaat het?', 'Hi', '**Wasssuup!**']
    await ctx.send(choice(responses))

@client.command(name='die', help='Deze command zegt een random woord')
async def die(ctx):
    responses = ['why have you brought my short life to an end', 'i could have done so much more', 'i have a family, kill them instead']
    await ctx.send(choice(responses))

@client.command(name='credits', help='Deze command zegt de eigenaar van deze bot')
async def credits(ctx):
    await ctx.send('Made by `Usopp`')
    await ctx.send('Thanks to `Passkall` for coming up with the idea')
    await ctx.send('Thanks to `Usopp` for helping with the `?die` and `?creditz` command')

@client.command(name='creditz', help='Deze command zegt de echte maker van deze bot')
async def creditz(ctx):
    await ctx.send('**No one but usopp!!**')

@client.command(name='play', help='Deze command speelt music')
async def play(ctx, url):
    if not ctx.message.author.voice:
        await ctx.send("Je zit niet in een voice channel :smile:")
        return

    else:
        channel = ctx.message.author.voice.channel

    await channel.connect()

    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=client.loop)
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    await ctx.send('**Now playing:** {}'.format(player.title))

@client.command(name='stop', help='Deze command laat de bot stoppen (de muziek stoppen)')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()

@tasks.loop(seconds=20)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(status)))




client.run("ODc1MTA4OTUxODk5OTIyNDQz.YRQuuA.4uVbZV3BbmXmASA5af0o1GPtD_E")
