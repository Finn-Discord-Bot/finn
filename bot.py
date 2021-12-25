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
async def _Ping(ctx: SlashContext):
    embed = discord.Embed(
        title="embed test",
        description = "this is just a test")  
    await ctx.send(content="hello", embeds=[embed])


@slash.slash(name="lasttradingday", description="Displays the last completed trading day")
async def _Lasttradingday(ctx: SlashContext):
    last_trade_day = last_trading_day()
    embed = discord.Embed(
        title="Last Trading Day",
        description=last_trade_day,
        color = discord.Color.from_rgb(131, 214, 129))
    await ctx.send(embeds=[embed])


@slash.slash(name="help", description = "Provides a list of possible commands")
async def _Help(ctx: SlashContext):
    embed = discord.Embed(
        title = "Commands",
        description = 
        """
        You seem to need a bit of assistance! Don't worry, grab some milk and cookies, sit back and relax. What do you need help with? :) \n 
        ==========================================
        \n /help - Provides a list of possible commands \n """,
        color=discord.Color.from_rgb(235, 168, 96)
        )

    embed.add_field(name ='Portfolio Commands', value = 
    """/createportfolio - Creates a portfolio \n /displayportfolio - Displays a portfolio \n
    """, inline=True)   

    embed.add_field(name = 'Finance Commands', value = 
    """/lasttradingday - Displays the last completed trading day \n /stockinfo - Displays an information preview of the specified ticker \n""", inline=True)

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
async def _Testinput(ctx: SlashContext, ticker_list: str):
    await ctx.send(content=f"I got you, you said {ticker_list}!")

@slash.slash(
    name = 'priceWeightedIndex',
    description = 'Command that creates a price weighted portfolio',
    guild_ids = guilds,
    options = [
        create_option(
            name="tickerlist",
            description="Enter a space-seperated list of tickers.",
            option_type=3,
            required=True
        )
    ]
)
async def _PriceWeightedIndex(ctx: SlashContext, tickerlist: str):
    temp = []
    temp = tickerlist.split()
    pw_portfolio = price_weighted(tickerlist)
    color=discord.Color.from_rgb(224, 255, 201)

    await ctx.send(content='hi')

    

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
    user_id = ctx.author.id
    temp = tickerlist.split()
    # portfolio should be a tuple with (actualportfolio, date)
    portfolio = portfolio_maker(tickerlist, portfoliotype, money)
    date = all_data[1]
    actualportfolio = all_data[0]
    add_portfolio(portfolio, user_id, date)
    color=discord.Color.from_rgb(207, 189, 255)
    
    #await ctx.send(content=f"I got you, you said {portfoliotype, tickerlist, str(money)}!")


@slash.slash(
    name = "companyinfo",
    description = "Command that provides the location, industry, and market capitalization of a given stock",
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
    
async def _CompanyInfo(ctx: SlashContext, ticker: str):
    ticker = ticker.upper()
    comp_info = company_info(ticker)
    location = comp_info[0]
    industry = comp_info[1]
    market_cap = comp_info[2]

    embed = discord.Embed(
        title = f'Company Information for {ticker}',
        description = 'The location of the company, industry of the company and its market capitalization.',
        color=discord.Color.from_rgb(255, 207, 233)
    )
    embed.set_author(name = 'Finn Bot')
    embed.add_field(name = 'Company Location', value = location, inline=True)
    embed.add_field(name = 'Company Industry', value = industry, inline=True)
    embed.add_field(name = 'Maket Capitalization', value = market_cap, inline=True)
    
    await ctx.send(embeds=[embed])


@slash.slash(
    name = "displayportfolio",
    description = "Command associated with displaying portfolio",
    guild_ids = guilds
)
async def _Displayportfolio(ctx: SlashContext):
    user_id = ctx.author.id
    portfolio_dict = get_portfolio(user_id)
    data = portfolio_graphs(portfolio_dict, user_id)
    initial_investment = data[0]
    current_value = data[1]
    net_return = current_value - initial_investment
    pct_return = 100 * current_value/initial_investment 
    color=discord.Color.from_rgb(255, 245, 189)
    
    embed = discord.Embed(
        title = "Portfolio Returns",
        description = "Here's your graph bro.",
        colour = discord.Color.from_rgb(187, 242, 229)    
    )
    embed.set_author(name ='Finn Bot')
    embed.add_field(name ='Initial Investment', value = initial_investment, inline=True)
    embed.add_field(name ='Current Value', value = current_value, inline=True)
    embed.add_field(name ='Net Return', value = net_return, inline=True)
    embed.add_field(name ='% Return', value = pct_return, inline=True)
    await ctx.send(embeds=[embed], file=discord.File(f'process/{user_id}.png'))
    os.remove(f'process/{user_id}.png')


    # await ctx.send(content=f"I've caught your uuid in 4K: {user_id}!")


# slash command for stock info
@slash.slash(
    name = "stockInfo",
    description = "Here is the preview of the specified ticker.",
    guild_ids = guilds,
    options = [
        create_option(
            name = "ticker",
            description = "What Ticker would you like to search?",
            required = True,
            option_type = 3
        ),
        create_option(
            name = "price",
            description = "What price would you like to search?",
            required=True,
            option_type = 4
            
        )
    ]
)
async def _StockInfo(ctx:SlashContext, ticker: str, price:int):
    ticker = ticker.upper()
    response = discord.Embed(
        title = f"{ticker} Info",
        description = "Description",
        colour = discord.Color.from_rgb(235, 121, 96)    
    )
    
    data = stock_info(ticker)
    response.set_author(name="Finn Bot")
    response.add_field(name='Beta', value=data['Beta'], inline=True)
    response.add_field(name='STD', value=data['STD'], inline=True)
    response.add_field(name='52Wk High', value=data['52Wk High'], inline=True)
    response.add_field(name='52Wk Low', value=data['52Wk Low'], inline=True)
    response.add_field(name='Last Trading Day Open', value=data['Last Trading Day Open'], inline=True)
    response.add_field(name='Last Trading Day Close', value=data['Last Trading Day Close'], inline=True)
    await ctx.send(embed=response)

#slash command for stock history (HAVEN'T BEEN TESTED YET)
@slash.slash(
    name = 'stockhistory',
    description = "Here is your stock's history.",
    guild_ids = guilds,
    options = [
        create_option(
            name = "ticker",
            description = "What ticker would you like to search?",
            required = True,
            option_type = 3
        )
    ]
)
async def _StockHistory(ctx: SlashContext, ticker: str, start_date: str, end_date: str):
    ticker = ticker.upper() 
    response = discord.Embed(
        title = f"{ticker} History",
        description = "Description",
        colour = discord.Color.from_rgb(235, 121, 96)
    )

    data = stock_history(ticker, start_date, end_date)
    response.set_author(name="Finn Bot")
    response.add_field(name="Open", value=data["Open"], inline=True)
    response.add_field(name="Close", value=data["Close"], inline=True)
    response.add_field(name="High", value=data["High"], inline=True)
    response.add_field(name="Low", value=data["Low"], inline=True)
    response.add_field(name="Volume", value=data["Volume"], inline=True)
    response.add_field(name="Dividends", value=data["Dividends"], inline=True)
    response.add_field(name="Stock Splits", value=data["Stock Splits"], inline=True)
    await ctx.send(embed=response)

# slash command for options (HAVEN'T BEEN TESTED YET)
@slash.slash(
    name = "options",
    description = "Here is the preview of the options available for your stock",
    guild_ids = guilds,
    options = [
        create_option(
            name = "ticker",
            description = "What Ticker would you like to search?",
            required = True,
            option_type = 3
        ),

        create_option(
            name = "range",
            description = "What range are you looking in?",
            required = True,
            option_type = 4
        ),
        create_option(
            name = "put_or_call",
            description = "Are you looking for a put or call option?",
            required = True,
            option_type = 3,
            choices = [
                create_choice(
                    name = "put",
                    value = "put"
                ),
                create_choice(
                    name = "call",
                    value = "call"
                )        
            ]
        )
    ]
)
async def _Options(ctx:SlashContext, ticker: str, range: int, put_or_call: str):
    ticker = ticker.upper()
    response = discord.Embed(
        title = f"{ticker} Info",
        description = "Description",
        colour = discord.Color.from_rgb(235, 121, 96)    
    )
    
    data = options(ticker, range_length, put_call)
    response.set_author(name="Finn Bot")
    response.add_field(name='Contract Symbol', value=data['contractSymbol'], inline=True)
    response.add_field(name='Last Trade Date', value=data['lastTradeDate'], inline=True)
    response.add_field(name='Strike', value=data['strike'], inline=True)
    response.add_field(name='Last Price', value=data['lastPrice'], inline=True)
    response.add_field(name='Bid', value=data['bid'], inline=True)
    response.add_field(name='Ask', value=data['ask'], inline=True)
    response.add_field(name='Change', value=data['change'], inline=True)
    response.add_field(name='Pct Change', value=data['percentChange'], inline=True)
    response.add_field(name='Volume', value=data['volume'], inline=True)
    response.add_field(name='Open Interest', value=data['openInterest'], inline=True)
    response.add_field(name='Implied Volatility', value=data['impliedVolatility'], inline=True)
    response.add_field(name='In the money?', value=data['inTheMoney'], inline=True)
    await ctx.send(embed=response)



# slash command for sharpe ratio (not tested)
@slash.slash(
    name = "sharperatio",
    description = "Command that provides the sharpe ratio of a stock",
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
async def _Sharperatio(ctx:SlashContext, ticker:str, start_date:str, end_date:str):
    ticker = ticker.upper()
    response = discord.Embed(
        title = f"{ticker} Sharpe Ratio",
        description = "Command that provides the sharpe ratio of a stock",
        colour = discord.Color.from_rgb(235, 121, 96)
    )
    ratio = sharpe_ratio(ticker, start_date, end_date)
    response.set_author(name='Finn Bot')
    response.add_field(name='Sharpe Ratio', value = ratio)
    await ctx.send(embed=response)

# slash command for correlation (not tested)
#@slash.slash(
#    name = "correlation",
#    description = "Command that returns the correlation of two stocks",
#    guild_ids = guilds,
#    options = [
#        create_option(
#            name = "ticker1",
 #           description = "What Ticker would you like to search?",
  #          required = True,
   #         option_type = 3
    #    ),
     #   create_option(
      #      name = "ticker2",
      #      description = "What Ticker would you like to search?",
       #     required=True,
        #    option_type = 3
        #)
    #]
#)
#async def _Correlation(ctx:SlashContext, ticker1: str, ticker2: str):
#    ticker1 = ticker1.upper()
#    ticker2 = ticker2.upper()
#    response = discord.Embed(
#        title = f"{ticker1} and {ticker2} Info",
#        description = ""
#    )


 



# Functions from the finance file 



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
    await bot.change_presence(activity=discord.Game('Listening for holiday STOCKings | prefix: /'), status="dnd")
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







    