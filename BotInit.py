import discord
from discord.ext import commands
import ChatHelper 
import Info


class BotAuth:
    def __init__(self):
        self.bot = commands.Bot(command_prefix='$')
        self.info = Info.ServerInformation("Data Files/server_info.json")


class MusicBot(BotAuth):
    def __init__(self):
        super().__init__()
        self.bot = commands.Bot(command_prefix='$',intents=discord.Intents().all())
        print("Started Music Bot")

        self.bot.add_cog(ChatHelper.ChatCommands(self.bot))        
        self.key = self.info.server_info["music_bot_api_key"]
        



