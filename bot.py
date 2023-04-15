import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from music_cog import music_cog
from help_cog import help_cog
load_dotenv()

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True

bot = commands.Bot(command_prefix='-', intents=intents)
bot.remove_command('help')
@bot.event
async def on_ready():
    print(f'{bot.user.name} is online.')
    await bot.add_cog(music_cog(bot))
    await bot.add_cog(help_cog(bot))

bot.run(os.environ['BOT_TOKEN'])
