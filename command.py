from discord.ext import commands #allows us to use command

bot = commands.Bot(command_prefix='$') #a command always starts with a prefix $
@bot.command()
async def create(arg):
     if arg == 'create'
          await arg.send()
