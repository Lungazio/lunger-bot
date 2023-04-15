from ast import alias
import discord
from discord.ext import commands
import os
from yt_dlp import YoutubeDL
import asyncio


discord.opus.load_opus('/opt/homebrew/lib/libopus.dylib')

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
        #all the music related stuff
        self.is_playing = False
        self.is_paused = False

        # 2d array containing [song, channel]
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        self.FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_delay_max 5 -nostdin',
    'options': '-vn'
}


        self.vc = None

     #searching the item on youtube
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception:
                return False

        # Find the best format with 'm4a' or 'webm' extension
        selected_format = None
        for format in info['formats']:
            if format['ext'] in ('m4a', 'webm'):
                if selected_format is None or ('abr' in format and 'abr' in selected_format and format['abr'] > selected_format['abr']):
                    selected_format = format

        if selected_format is None:
            return False

        return {'source': selected_format['url'], 'title': info['title']}



    def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            #get the first url
            m_url = self.music_queue[0][0]['source']
            song_title = self.music_queue[0][0]['title']
            current_ctx = self.music_queue[0][2]  # Added this line to get the current context

            #remove the first element as you are currently playing it
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())

            # Added this line to announce the currently playing song
            asyncio.run_coroutine_threadsafe(current_ctx.send(f"Now playing: {song_title}"), self.bot.loop)
        else:
            self.is_playing = False
            asyncio.run_coroutine_threadsafe(self.vc.disconnect(), self.bot.loop)



    # infinite loop checking 
    async def play_music(self, ctx, added_to_queue=True):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']

            # try to connect to voice channel if you are not already connected
            if self.vc == None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                # in case we fail to connect
                if self.vc == None:
                    await ctx.send("Could not connect to the voice channel")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])

            # remove the first element as you are currently playing it
            song_title = self.music_queue[0][0]['title']
            self.music_queue.pop(0)

            # announce the song that is playing
            if added_to_queue:
                await ctx.send(f"Now playing: {song_title}")
            else:
                await ctx.send(f"{song_title} added to the queue")
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.is_playing = False



    @commands.command(name="play", aliases=["p","playing"], help="Plays a selected song from youtube")
    async def play(self, ctx, *args):
        query = " ".join(args)

        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            # you need to be connected so that the bot knows where to go
            await ctx.send("Connect to a voice channel!")
        elif self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("Could not download the song. Incorrect format try another keyword. This could be due to playlist or a livestream format.")
            else:
                print(song)
                song_title = song['title']  # Get the song title
                await ctx.send(f"{song_title} added to the queue")  # Display the song title in the message
                self.music_queue.append([song, voice_channel, ctx])  # Add ctx to the music_queue

                if self.is_playing == False:
                    await self.play_music(ctx)

    @commands.command(name="yk",  help="Plays a selected song from youtube")
    async def yk(self, ctx, *args):
        query = "imagine dragons"
        
        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            #you need to be connected so that the bot knows where to go
            await ctx.send("Connect to a voice channel!")
        elif self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("Could not download the song. Incorrect format try another keyword. This could be due to playlist or a livestream format.")
            else:
                print(song)
                await ctx.send("Yin Khai song added to the queue")
                self.music_queue.append([song, voice_channel,ctx])
                
                if self.is_playing == False:
                    await self.play_music(ctx)

    @commands.command(name="jr",  help="Plays a selected song from youtube")
    async def jr(self, ctx, *args):
        query = "plain jane asap ferg"
        
        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            #you need to be connected so that the bot knows where to go
            await ctx.send("Connect to a voice channel!")
        elif self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("Could not download the song. Incorrect format try another keyword. This could be due to playlist or a livestream format.")
            else:
                print(song)
                await ctx.send("Ronald song added to the queue")
                self.music_queue.append([song, voice_channel,ctx])
                
                if self.is_playing == False:
                    await self.play_music(ctx)

    @commands.command(name="pause", help="Pauses the current song being played")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name = "resume", aliases=["r"], help="Resumes playing with the discord bot")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name="skip", aliases=["s"], help="Skips the current song being played")
    async def skip(self, ctx):
        if self.vc != None and self.vc:
            self.vc.stop()

    @commands.command(name="queue", aliases=["q"], help="Displays the current songs in queue")
    async def queue(self, ctx):
        if len(self.music_queue) == 0:
            await ctx.send("No music in queue")
            return

        queue_list = ""
        for i, song in enumerate(self.music_queue[:6]):
            queue_list += f"{i+1}. {song[0]['title']}\n"
        await ctx.send(f"```{queue_list}```")



    @commands.command(name="remove", aliases=["x"], help="Removes a song from the queue")
    async def remove(self, ctx, index: int):
        if index < 1 or index > len(self.music_queue):
            await ctx.send("Invalid index")
            return

        removed_song = self.music_queue.pop(index - 1)
        await ctx.send(f"Removed \"{removed_song[0]['title']}\" from the queue")



    @commands.command(name="clear", aliases=["c", "bin"], help="Stops the music and clears the queue")
    async def clear(self, ctx):
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("Music queue cleared")

    @commands.command(name="leave", aliases=["disconnect", "l", "d"], help="Kick the bot from VC")
    async def dc(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()