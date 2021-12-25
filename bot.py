import discord
from discord.ext import commands
from discord import guild
from discord_slash import SlashCommand, SlashContext
from discord_slash.model import GuildPermissionsData
from discord_slash.utils.manage_commands import create_choice, create_option
import datetime
import json
import os
import asyncio

from finance_functions import *
from connect_database import *
# from smart_weights import *

TEST = True

try:
    conf = json.load(open("config/config.json"))
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
guilds = []

def get_guilds():
    return [g.id for g in bot.guilds]

dmfailed = discord.Embed(
    title="DM Failed",
    description='',
    timestamp=datetime.utcnow(),
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

# # Take in user input and store it
# @bot.command()
# async def repeat(ctx):
#     await ctx.message.delete()
#     embed = discord.Embed(
#         title = "Please send a message",
#         description = "Please do so within 10 seconds"
#     )
#     sent = await ctx.send(embed = embed)
#     try:
#         msg = await bot.wait_for(
#             "message",
#             timeout=10,
#             check = lambda message: message.author == ctx.author and message.channel == ctx.channel

#         )
#         if msg:
#             await sent.delete()
#             await msg.delete()
#             await ctx.send(msg.content)
#     except asyncio.TimeoutError:
#         await sent.delete()
#         await ctx.send("Cancelling due to Timeout",delete_after = 10)
    

# Slash Commands
@slash.slash(name="ping", description="Ping command")
async def _ping(ctx: SlashContext):
    embed = discord.Embed(
        title="embed test",
        description = "this is just a test")  
    await ctx.send(content="hello", embeds=[embed])


@slash.slash(name="lasttradingday", description="Displays the last completed trading day")
async def _lasttradingday(ctx: SlashContext):
    last_trade_day = last_trading_day()
    embed = discord.Embed(
        title="Last Trading Day",
        description=last_trade_day,
        color = discord.Color.from_rgb(131, 214, 129))
    await ctx.send(embeds=[embed])


@slash.slash(name="help", description = "Provides a list of possible commands")
async def _help(ctx: SlashContext):
    embed = discord.Embed(
        title = "Commands",
        description = 
        """
        You seem to need a bit of assistance! 
        Don’t worry, grab some milk and cookies, sit back and relax. 
        What do you need help with? \n 
        ==========================================================
        /help - Provides a list of possible commands \n """,
        color=discord.Color.from_rgb(235, 168, 96)
        )

    embed.add_field(name ='Portfolio Commands', value = 
    """\n /createportfolio - Command associated with portfolio creation \n 
    /displayportfolio - Command associated with displaying portfolio \n""", inline=True)   

    embed.add_field(name = 'Finance Commands', value = 
    """\n /lasttradingday - Displays the last completed trading day \n
    /stockinfo - Displays an information preview of the specified ticker \n""", inline=True)

    embed.set_image(url='https://cdn.discordapp.com/attachments/846084093065953283/924129382090539038/IMG_0005.jpg') 
    await ctx.send(embeds=[embed])
        
        
        
        # FINISH THIS LATER WHEN ALL COMMANDS ARE DONE 
        # MAKE HEADERS - Finance commands, stock commands, Portfolio commands, Misc Bot commands 
    


# User Input
@slash.slash(
    name = "testinput",
    description = "this just just a test but with *-+= inputs =+-*",
    options=[
        create_option(
            name="ticker_list",
            description="This is the first option we have.",
            option_type=3,
            required=True)],
    guild_ids = guilds
)
async def _testinput(ctx: SlashContext, ticker_list: str):
    await ctx.send(content=f"I got you, you said {ticker_list}!")

    

@slash.slash(
    name = "CreatePortfolio",
    description = "Command associated with portfolio creation",
    guild_ids = guilds,
    options=[
        create_option(
            name="portfoliotype",
            description="What type of portfolio would you like to create?",
            option_type=3,
            required=True,
            choices = [
                create_choice(
                    name = "Price Weighted Index",
                    value = "PRICE WEIGHTED"
                ),
                create_choice(
                    name = "Market-Capitalization Weighted Index",
                    value = "MARKET WEIGHTED"
                ),
                create_choice(
                    name = "Risky Smart Weighted Portfolio",
                    value = "RISKY"
                ),
                create_choice(
                    name = "Safe Smart Weighted Portfolio",
                    value = "SAFE"
                )
            ]
        ),
        create_option(
            name="tickerlist",
            description="Enter a space-seperated list of tickers.",
            option_type=3,
            required=True
        ),
        create_option(
            name="money",
            description="The total amount of money you want to invest (Dollars).",
            option_type=4,
            required=True
        )
    ]
)
async def _CreatePortfolio(ctx: SlashContext, portfoliotype: str, tickerlist: str, money: int):
    await ctx.send(content=f"I got you, you said {portfoliotype, tickerlist, str(money)}!")

@slash.slash(
    name = "displayportfolio",
    description = "Command associated with displaying portfolio",
    guild_ids = guilds
)
async def _displayportfolio(ctx: SlashContext):
    user_id = ctx.author.id
    portfolio_dict = get_portfolio(user_id)
    print(portfolio_dict)
    regenerate_portfolio(portfolio_dict)
    # #Get portfolio using user_id
    # ...
        
    #await ctx.send(file=discord.File(f'process/{user_id}.png'))
    #os.remove(f'process/{user_id}.png')


    # await ctx.send(content=f"I've caught your uuid in 4K: {user_id}!")


# slash command for stock info
@slash.slash(
    name = "StockInfo",
    description = "Here is the preview of the specified ticker.",
    guild_ids = guilds,
    options = [
        create_option(
            name = "ticker",
            description = "What Ticker would you like to search?",
            required = True,
            option_type = 3
        )
    ]
)
async def _StockInfo(ctx:SlashContext, ticker: str):
    ticker = ticker.upper()
    response = discord.Embed(
        title = f"{ticker} Info",
        description = "Description",
        colour = discord.Color.from_rgb(235, 121, 96)    
    )
    
    data = stock_info(ticker)
    response.set_footer(text="footer")
    response.set_author(name="Finn Bot")
    response.add_field(name='Beta', value=data['Beta'], inline=True)
    response.add_field(name='STD', value=data['STD'], inline=True)
    response.add_field(name='52Wk High', value=data['52Wk High'], inline=True)
    response.add_field(name='52Wk Low', value=data['52Wk Low'], inline=True)
    response.add_field(name='Last Trading Day Open', value=data['Last Trading Day Open'], inline=True)
    response.add_field(name='Last Trading Day Close', value=data['Last Trading Day Close'], inline=True)
    await ctx.send(embed=response)

# # Test - just making sure i understand 
# @slash.slash(
#     name = "gettinginfo",
#     description = "Getting some info of the server",
#     guild_ids = guilds
# )
# #testFunc("AAPL")
# async def _gettinginfo(ctx : SlashContext):
#     name = str(ctx.guild.name)
#     description = str(ctx.guild.description)
#     serverID = str(ctx.guild.id)
#     memberCount = str(ctx.guild.member_count)
#     picture = str(ctx.guild.icon_url)

#     embed = discord.Embed(
#         title = name,
#         description = description
#     )
#     embed.set_thumbnail(url=picture)
#     embed.add_field(name = "Server ID", value = serverID, inline = True)
#     embed.add_field(name = "# of Members", value = memberCount, inline = True)
#     await ctx.send(content = 'gettinginfo', embed=embed)


# Code to upload matplotlib figs
"""
@bot.command()
async def history(ctx):
    # Uploads a graphic sunmmarizing your mood over the past seven days.
    user_id = ctx.message.author.id
    weekly_moods(get_moods(user_id), user_id) # Creates a png into the process directory
    await ctx.send(file=discord.File(f'process/{user_id}.png')) # Once it's made, it just uploads it
    os.remove(f'process/{user_id}.png') # And then it will delete it
"""


# Events
@bot.event
async def on_ready():
    if not os.path.exists('process'):
        os.mkdir('process')
    await bot.change_presence(activity=discord.Game('Listening for poetry skills | prefix: >'), status="dnd")
    print('Bot Initialized')


@bot.event
async def on_guild_join(guild):
    if guild.id not in guilds:
        guilds.append(guild.id)
    print(guilds)
        

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







    