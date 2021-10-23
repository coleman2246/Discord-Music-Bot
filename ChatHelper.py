from discord.ext import commands, tasks
import discord
import Info
import json
import asyncio
import numpy as np
import youtube_dl as yt 
import discord.utils

class ChatCommands(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.info = Info.ServerInformation("Data Files/server_info.json")

        self.audio_q = {}
        self.audio_q_lock = {} 


    @commands.command()
    async def play(self,ctx,url):
        await self.bot.wait_until_ready()
        if ctx.author.voice == None:
            await ctx.channel.send("{} you are not a in a voice channel".format(ctx.author.mention))
            return 
        vc = ctx.author.voice.channel
        instance = {"ctx" : ctx, "url": url,"skip" : False}
        if vc.id not in self.audio_q.keys():
            self.audio_q[vc.id] = []

        if vc.id not in self.audio_q_lock.keys():
            self.audio_q_lock[vc.id] = asyncio.Lock()

        
        await self.audio_q_lock[vc.id].acquire()

        self.audio_q[vc.id].append(instance)

        if len(self.audio_q[vc.id]) == 1:
            self.audio_q_lock[vc.id].release()

            asyncio.Task(self.play_audio(vc))
            #loop = asyncio.get_event_loop()
            #loop.create_task(self.play_audio(vc))
        else:
            self.audio_q_lock[vc.id].release()
        await ctx.channel.send("{} added to queue".format(url))

    @commands.command()
    async def skip(self,ctx):
        if ctx.author.voice == None:
            await ctx.channel.send("{} you are not a in a voice channel".format(ctx.author.mention))
            return 
        vc = ctx.author.voice.channel

        if vc.id not in self.audio_q.keys() or len(self.audio_q[vc.id]) == 0:
            await ctx.channel.send("Queue is Empty")
        else:

            await self.audio_q_lock[vc.id].acquire()            
            self.audio_q[vc.id][0]["skip"] = True
            self.audio_q_lock[vc.id].release()

            await ctx.channel.send("Queue is now of size {}".format(len(self.audio_q[vc.id])-1 ))

    @commands.command()
    async def stop(self,ctx):
        if ctx.author.voice == None:
            await ctx.channel.send("{} you are not a in a voice channel".format(ctx.author.mention))
            return 
        vc = ctx.author.voice.channel

        if vc.id not in self.audio_q.keys() or len(self.audio_q[vc.id]) == 0:
            await ctx.channel.send("Queue is Empty")
        else:
            await self.audio_q_lock[vc.id].acquire()            
            self.audio_q[vc.id] = self.audio_q[vc.id][:1]
            self.audio_q[vc.id][0]["skip"] = True
            self.audio_q_lock[vc.id].release()

            await ctx.channel.send("Stopped audio")




    # todo do url verifying
    async def play_audio(self,vc):
        await self.audio_q_lock[vc.id].acquire()
        is_not_empty = len(self.audio_q[vc.id]) > 0
        self.audio_q_lock[vc.id].release()

        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist':'True',
            'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '96' }]}
        while is_not_empty:
            
            
            url = self.audio_q[vc.id][0]["url"]
            with yt.YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
                I_URL = info['formats'][0]['url']

                source = await discord.FFmpegOpusAudio.from_probe(I_URL, **FFMPEG_OPTIONS)

                voice = discord.utils.get(self.bot.voice_clients, guild=self.audio_q[vc.id][0]["ctx"].guild) # This allows for more functionality with voice channels
                if voice == None:
                    bot_voice = await vc.connect()
                    
                else:
                    if not voice.is_connected():
                        bot_voice = await vc.connect()
                    else:
                        bot_voice = voice
                        
                player = bot_voice.play(source)
                print(bot_voice.is_playing())
                
                while bot_voice.is_playing(): 
                    await self.audio_q_lock[vc.id].acquire()
                    if self.audio_q[vc.id][0]["skip"]:
                        bot_voice.stop()
                    self.audio_q_lock[vc.id].release()

                    await asyncio.sleep(1)

                await self.audio_q_lock[vc.id].acquire()
                self.audio_q[vc.id].pop(0)
                is_not_empty = len(self.audio_q[vc.id]) > 0
                self.audio_q_lock[vc.id].release()

        
        voice = discord.utils.get(self.bot.voice_clients, guild=vc.guild) # This allows for more functionality with voice channels
        if voice != None and voice.is_connected():
                await voice.disconnect()
            
