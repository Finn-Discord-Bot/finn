import yfinance as yf
import matplotlib.pyplot as plt
import numpy as npf
import pandas as pd
import datetime 
from datetime import date, datetime, timedelta, timezone
from smart_weights import *

# Variables
# Will have to globalize the yfinance data too cause having to constantly do api calls is going to make our code really slow
global stock 
global stock_info


# two step process
# 1. Input a ticker
# 2. Then the user will input the function 


def last_trading_day():
    now = datetime.now(timezone(timedelta(hours=-5), 'EST'))

    # US Markets close at 4pm, but afterhours trading ends at 8pm.
    # yFinance stubbornly only gives the day's data after 8pm, so we will wait until 9pm to pull data from
    # the current day.
    market_close = now.replace(hour=21, minute=0, second=0, microsecond=0)
    if now < market_close:
        DELTA = 1
    # If it is saturday or sunday
    elif now.weekday() >= 5:
        DELTA = 1
    else:
        DELTA = 0
        
    start_date = (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d")
    end_date = (datetime.now() - pd.tseries.offsets.BDay(DELTA)).strftime("%Y-%m-%d")
    MarketIndex = "^GSPC" # We can use the S&P 500's data to see the last day where we have data

    market_hist = yf.Ticker(MarketIndex).history(start=start_date, end=end_date).filter(like="Close").dropna()   

    latest_day = market_hist.index[-1]
    return latest_day.strftime("%Y-%m-%d")


# Stock Info (Open, High, Low, Close, Volume, Dividends, Stock Splits)

def stock_info(ticker):
    stock = yf.Ticker(ticker)
    return stock 

# stock = stock_info()
# stock_info = stock.info
    

def stock_info(ticker):
    stock = yf.Ticker(ticker)
    stock_info = stock.info
    stock_open = stock_info["open"]
    stock_close = stock_info["close"]
    return[stock_open, stock_close]


# PyZipFile Class for creating ZIP archives containing Python libraries.     class zipfile.ZipInfo(filename='NoName', date_time=, 1980, 1, 1, 0, 0, 0)
# Stock History 

def valid_ticker_list(ticker_list):
    ticker_hist = yf.download(
                    tickers = " ".join(ticker_list),
                    # Download Data From the past 6 months
                    period = "6mo",
                    interval = "1d",
                    group_by = 'tickers',
                    threads = True
                )
    return list(dict.fromkeys([t[0] for t in ticker_hist.dropna(axis=1, how='all').columns]))


class Portfolio:
    
    def __init__(self, ticker_list, start_date, end_date, starting_balance):
        self.set_start_date(start_date)
        self.set_end_date(end_date)
        self.set_ticker_list(ticker_list)
        self.starting_balance = starting_balance

    # Setters
    def set_ticker_list(self, ticker_list):
        self.ticker_list = ticker_list

    def set_start_date(self, start_date):
        self.start_date = start_date
    
    def set_end_date(self, end_date):
        self.end_date = end_date

    def set_starting_balance(self, starting_balance):
        self.starting_balance = starting_balance
    

    # Getters
    #def get_ticker_list(self):
       # return self.__ticker_list

    #def add_ticker(self, ticker):
    #    ticker_list.append(ticker)

    # Functions

    def add_ticker(self, ticker):
        self.ticker_list.append(ticker)


def stock_history(ticker, start_date, end_date):
    current_date = date.today()
    if start_date == "" or end_date == "":
        stock_history = stock.history(start = date.today, end = date.today) 
    else:
        stock_history = stock.history(start = start_date, end = end_date) 


def price_weighted(ticker_list, start_date, end_date):

    # Create DataFrame
    pw_portfolio = pd.DataFrame()
    num_tickers = len(ticker_list)

    # Add Close price columns for each stock
    for i in range(len(ticker_list)):
        ticker_hist = ticker_list[i].history(start = start_date, end = end_date)
        pw_portfolio[f'{ticker_list[i]} Close'] = ticker_hist.Close
    
    # Get Price Weighted Index
    pw_portfolio['Price Weighted Index'] = (pw_portfolio.sum(axis=1))/num_tickers

    return pw_portfolio

def make_price_weighted_portfolio(investment, ticker_list, start_date, end_date):

    # Create DataFrame
    pw_portfolio = pd.DataFrame()
    num_tickers = len(ticker_list)
    pw_portfolio['Tickers'] = ticker_list
    value_per_stock = investment/num_tickers

    # Add Close price columns for each stock
    for i in range(len(ticker_list)):
        ticker_hist = ticker_list[i].history(start = start_date, end = end_date)
        pw_portfolio[f'{ticker_list[i]} Shares'] = value_per_stock/ticker_hist.Close

    return pw_portfolio


def market_weighted(ticker_list, start_date, end_date, starting_balance):
    
    stock_dict = {}
    totalMarketCap = 0
    for ticker in ticker_list:
        stock_dict[ticker] = yf.Ticker(ticker)
        stock_dict[f"{ticker} Shares Outstanding"] = stock_dict[ticker].info["sharesOutstanding"]
        stock_dict[f"{ticker} History"] = stock_dict[ticker].history(start = start_date, end = end_date).Close
        stock_dict[f"{ticker} Market Capitalization"] = stock_dict[f"{ticker} Shares Outstanding"] * stock_dict[f"{ticker} History"].iloc[0]
        totalMarketCap += stock_dict[f"{ticker} Market Capitalization"]
    
    ticker_list = ["AAPL", "GOOG", "TSLA"]
    market_weighted_df = pd.DataFrame(index = ticker_list)
    market_weighted_df.index.rename("Ticker", inplace = True)
    market_weighted_df["Shares"] = 0
    
    for ticker in ticker_list:
        stock_dict[f"{ticker} Market Capitalization Percent"] = stock_dict[f"{ticker} Market Capitalization"] / totalMarketCap
        #print(stock_dict[f"{ticker} Market Capitalization Percent"])
        #print(stock_dict[f"{ticker} Market Capitalization Percent"] * starting_balance)
        market_weighted_df.loc[ticker,"Shares"] = (stock_dict[f"{ticker} Market Capitalization Percent"] * starting_balance) / stock_dict[f"{ticker} History"].iloc[0]
   
    return market_weighted_df
    
def portfolio_maker(ticker_list, start_date, end_date, weight_option):
    
    # Get valid ticker list
    valid_tickers = valid_ticker_list(ticker_list)

    if not valid_tickers:
        print('No valid tickers were inputted!')
        return None
    elif len(valid_tickers) > 10:
        print('Exceeded Maximum Number of Tickers!')
        return None
    else:
        # save weight option
        option = weight_option.upper()

        # check weight option
        if option == 'PRICE WEIGHTED':
            portfolio = make_price_weighted_portfolio(ticker_list, start_date, end_date)

        elif option == 'MARKET WEIGHTED':
            portfolio = market_weighted(ticker_list, start_date, end_date)

        else:
            portfolio = smart_weighted(ticker_list, start_date, end_date, option)
        
        if not portfolio:
            return None
        else:
            pass
        return True


# Earnings per Share/ Return on equity?


# Company info (location, industry, market capitalization)
def company_info(ticker):
    location = ticker.info['city'] + ", " + ticker.info['country']
    industry = ticker.info['industry']
    market_cap = ticker.info['marketCap']
    return [location, industry, market_cap]


def portfolio_graphs(ticker_list, start_date, end_date, weight_option, userid):

    # Get valid ticker list
    valid_tickers = valid_ticker_list(ticker_list)

    if not valid_tickers:
        print('Invalid tickers were inputted!')
    elif len(valid_tickers) > 10:
        print('Exceeded Maximum Number of Tickers!')
    else:

        # Create desired portfolio with ticker list
        portfolio = portfolio_maker(ticker_list, start_date, end_date, weight_option)

        weight = weight_option.upper()

        # Get monthly Data
        monthly_data = portfolio.resample('MS').first()
        
        if weight == 'PRICE WEIGHTED':
            
            # Initiate plot
            fig, ((ax1), (ax2)) = plt.subplot(2,1)
            fig.set_size_inches(20,20)

            fig.suptitle(f'{weight_option} Portfolio Returns: {start_date} to {end_date}')

            ax1.plot(portfolio.index, portfolio['Price Weighted Index'])
            ax1.set_title(f'Daily Portfolio Returns ({weight_option})')
            ax1.set_xlable('Dates')
            ax1.set_ylabel('Returns')
            
            ax2.plot(portfolio.index, monthly_data['Price Weighted Index'])
            ax2.set_title(f'Monthly Portfolio Value ({weight_option})')
            ax2.set_xlabel('Dates')
            ax2.set_ylabel('Returns')

            # Create png of graphs
            plt.savefig(f'process/{userid}.png')

        elif weight == 'MARKET WEIGHTED':

            # Initiate plot
            fig, ((ax1), (ax2)) = plt.subplot(2,1)
            fig.set_size_inches(20,20)

            fig.suptitle(f'{weight_option} Portfolio Returns: {start_date} to {end_date}')

            ax1.plot(portfolio.index, portfolio['Market Weighted Index'])
            ax1.set_title(f'Daily Portfolio Returns ({weight_option})')
            ax1.set_xlable('Dates')
            ax1.set_ylabel('Returns')
            
            ax2.plot(portfolio.index, monthly_data['Market Weighted Index'] )
            ax2.set_title(f'Monthly Portfolio Value ({weight_option})')
            ax2.set_xlabel('Dates')
            ax2.set_ylabel('Returns')

            # Create png of graphs
            plt.savefig(f'process/{userid}.png')
        
        elif weight == 'SMART WEIGHTED':

            # Initiate plot
            fig, ((ax1), (ax2)) = plt.subplot(2,1)
            fig.set_size_inches(20,20)

            fig.suptitle(f'{weight_option} Portfolio Returns: {start_date} to {end_date}')

            ax1.plot(portfolio.index, portfolio['Smart Weighted Index'])
            ax1.set_title(f'Daily Portfolio Returns ({weight_option})')
            ax1.set_xlable('Dates')
            ax1.set_ylabel('Returns')
            
            ax2.plot(portfolio.index, monthly_data['Smart Weighted Index'])
            ax2.set_title(f'Monthly Portfolio Value ({weight_option})')
            ax2.set_xlabel('Dates')
            ax2.set_ylabel('Returns')

            # Create png of graphs
            plt.savefig(f'process/{userid}.png')


# Beta Value        NOTE: .info returns a different value from the manual calculation
def beta(ticker, start_date, end_date):
    stock = yf.Ticker(ticker)
    market = yf.Ticker('^GSPC')
    today = date.today()
    tomorrow = today + datetime.timedelta(days = 1)
    
    if type(stock.info['beta']) == int or type(stock.info['beta']) == float:
        return stock.info['beta']
    else:
        # If no date was inputted, use data from today 
        if start_date == "" or end_date == "":
            stock_hist = stock.history(start = today, end = tomorrow)
            market_hist = market.history(start = today, end = tomorrow)

            prices = pd.DataFrame(stock_hist.Close) 
            prices.columns = [ticker]
            prices[market] = market_hist['Close']

            # Note: unable to take pct_change or covariance with only one day available
            returns = prices.iloc[0,0]
            market_var = prices.iloc[0,1]
            Beta = returns/market_var
            return Beta 
        else: 
            stock_hist = stock.history(start = start_date, end = end_date)
            market_hist = market.history(start = start_date, end = end_date)

            prices = pd.DataFrame(stock_hist.Close)
            prices.columns = [ticker]
            prices[market] = market_hist['Close']
            # Calculate monthly returns
            monthly_returns = prices.resample('M').ffill().pct_change()
            monthly_returns.drop(index=monthly_returns.index[0], inplace=True)
            # Calculate the market variance
            market_var = monthly_returns[market].var()
        
            # Calculate the ticker's beta value
            Beta = monthly_returns.cov()/market_var
            return Beta.iloc[0,1]      


# Sharpe Ratio
def sharpe_ratio(ticker, start_date, end_date):
    # For sharpe ratio we need a portfolio so for simplicity I will just let the portfolio just be 1 share of whatever we are interested in
    price_history = stock_history(ticker, start_date, end_date)

    sharpe_ratio = price_history['Close'].pct_change().mean() / price_history['Close'].pct_change().std()

    #Will have to double check if this actually works or not
    return sharpe_ratio
    
def pe_ratio(ticker_list):

    # Get valid ticker list
    valid_tickers = valid_ticker_list(ticker_list)

    if not valid_tickers:
        print('No valid tickers were inputted!')
    elif len(valid_tickers) > 10:
        print('Exceeded Maximum Number of Tickers!')
    else:
        share_price_sum = 0
        earnings_sum = 0

        for i in range(len(ticker_list)):
            ticker = yf.Ticker(ticker_list[i])
            ticker_info = ticker.info
            share_price_sum += ticker_info['currentPrice']
            earnings_sum += (ticker_info['grossProfits']/ticker_info['sharesOutstanding'])
    
    return share_price_sum/earnings_sum

# Options
#Requires the user to input a price range and put/call 
def options(ticker, price, range, put_call):
    stock = yf.Ticker(ticker)
    opt = stock.option_chain(stock.options[1])
    
    #If user wants put option or call option
    if put_call == "put":
        opt = pd.DataFrame().append(opt.puts)
    elif put_call == "call":
        opt = pd.DataFrame().append(opt.calls)

    #Grab inputted stock price. If no inputed stock price, use current stock price
    if price == "":
        stockSP = stock.info['currentPrice']
    else:
        stockSP = price

    #Determine and display the calls that meet the criteria that is $5 within the current price
    calls = opt.loc[((stockSP-range)<=opt['strike'])&((stockSP+range) >= opt['strike'])]

    #Double check if this actually works
    return calls


#Volatility (standard deviation)
def std(portfolio):

    monthly_returns = portfolio.resample('MS').first().pct_change()

    return monthly_returns.std() 


#Correlation with other stocks (need 2 tickers to be inputed)
def correlation(ticker1, ticker2):
    # get ticker info
    ticker1 = yf.Ticker(ticker1)
    ticker1_info = ticker1.info
    
    ticker2 = yf.Ticker(ticker2)
    ticker2_info = ticker2.info
    
    # check ticker validity, and proceeding  
    if ticker1_info['regularMarketPrice'] != None or ticker2_info['regularMarketPrice'] != None:
        from datetime import datetime
        start_date = '1900-01-01'
        now = datetime.now()
        end_date = now.strftime("%Y-%m-%d")
        un_ticker1_hist = ticker1.history(start = start_date, close = end_date)
        un_ticker2_hist = ticker2.history(start = start_date, close = end_date)
        if un_ticker1_hist.index[0].strftime("%Y-%m-%d") > un_ticker2_hist.index[0].strftime("%Y-%m-%d"):
            real_start_date = un_ticker2_hist.index[0].strftime("%Y-%m-%d")
        else:
            real_start_date = un_ticker1_hist.index[0].strftime("%Y-%m-%d")
        ticker1_hist = ticker1.history(start = real_start_date, close = end_date ,interval="1mo").dropna()
        ticker2_hist = ticker2.history(start = real_start_date, close = end_date, interval = "1mo").dropna()
        prices = pd.DataFrame(ticker1_hist['Close'])
        prices.columns = [ticker1]
        prices[ticker2] = ticker2_hist['Close']
        monthly_returns = 100 * prices.pct_change()[1:]
        print("Correlation:")
        print(100 * monthly_returns.corr().iat[0,1])

    else:
        print("Invalid Ticker(s). Please try again.")

# Different companies and fees