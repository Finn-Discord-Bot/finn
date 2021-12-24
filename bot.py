import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
import datetime
import json

# import finance_functions

TEST = True

try:
    conf = json.load(open("config.json"))
    if conf['token'] is None:
        raise Exception
    token = conf['token']
    if TEST:
        token = conf['token_test']
except Exception:
    print("Failed to open config, check it exists and is valid.")

#, intents=discord.Intents.all()
#, description="Finn"
bot = commands.Bot(command_prefix='>', intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)

check_reaction = '✅'

dmfailed = discord.Embed(
    title="DM Failed",
    description='',
    timestamp=datetime.datetime.utcnow(),
    color=discord.Color.from_rgb(240, 71, 71)
)


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


@bot.command()
async def pingdm(ctx):
    try:
        await ctx.author.send('pong')
        await ctx.message.add_reaction(check_reaction)
    except discord.Forbidden:
        await ctx.send(embed=dmfailed)
# Slash Commands
@slash.slash(name="ping", description="Ping command")
async def _ping(ctx: SlashContext):
    await ctx.send("Pong")
    
    # embed = discord.Embed(title="embed test")  
    # await ctx.send(content="hello", embeds=[embed])
    
# Events


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('Listening for poetry skills | prefix: >'), status="dnd")
    print('Bot Initialized')


@bot.listen()
async def on_message(message):
    message_content = message.content
    try:
        if message_content == "Hello" and not message.author.bot:
            await message.channel.send("Hello")
    except TypeError:
        return None


def start_bot():
    bot.run(token)