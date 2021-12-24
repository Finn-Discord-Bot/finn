import yfinance as yf
import matplotlib.pyplot as plt
import numpy as npf
import pandas as pd
import datetime 
from datetime import date
from smart_weights import *

# Variables
# Will have to globalize the yfinance data too cause having to constantly do api calls is going to make our code really slow
global stock 
global stock_info


# two step process
# 1. Input a ticker
# 2. Then the user will input the function 

# Stock Info (Open, High, Low, Close, Volume, Dividends, Stock Splits)

def stock_info(ticker):
    stock = yf.Ticker(ticker)
    return stock 

stock = stock_info
stock_info = stock.info
    

def stock_info(ticker):
    stock_open = stock_info["open"]
    stock_close = stock_info["close"]
    print(stock_open)
stock_info("AAPL")

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

             
def get_info(ticker):
    try: 
        ticker_info = tickers.tickers[ticker].info
        if "market" in ticker_info.keys():
            # Check if the stock is listed in the US market, and denominated in USD
            if ticker_info["market"] == 'us_market' and ticker_info["currency"] == 'USD':
                ticker_info_dict[ticker] = ticker_info
            else:
                print(f"Found {ticker} is not denominated in USD or in the US Market - Skipped")
    except KeyError as error:
        print(f'Error: Stock not found | Error - {ticker}: {error}')

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


def portfolio_add(ticker, ticker_list, portfolio):
    portfolio_maker(ticker)


def price_weighted(ticker_list, start_date, end_date):

    # Create DataFrame
    pw_portfolio = pd.DataFrame()

    num_tickers = len(ticker_list)

    # Add Close price columns for each stock
    for i in range(len(ticker_list)):
        ticker_hist = ticker_list[i].history(start = start_date, end = end_date)
        pw_portfolio[f'{ticker_list[i]} Close'] = ticker_hist.Close
    
    # Get Price Weighted Index
    for i in range(len(ticker_list)):
        pw_portfolio['Price Weighted Index'] = (pw_portfolio.sum(axis=1))/num_tickers
    
    return pw_portfolio


def market_weighted(ticker_list, start_date, end_date):
    
    close_df = pd.DataFrame()
    for i in range(len(ticker_list)):
        ticker_obj[i] = yf.Ticker(ticker_list[i])
        sharesOut[i] = ticker_obj[i].info['sharesOutstanding']
        close_df["Close{0}".format(i)] = ticker_list[i].history(start = start_date, end = end_date).Close


def portfolio_maker(ticker_list, start_date, end_date, weight_option):
    
    # Get valid ticker list
    valid_tickers = valid_ticker_list(ticker_list)

    if not valid_tickers:
        print('No valid tickers were inputted!')
    elif len(valid_tickers) > 10:
        print('Exceeded Maximum Number of Tickers!')

    else:
        # save weight option
        option = weight_option.upper()

        # check weight option
        if option == 'PRICE WEIGHTED':
            price_weighted(ticker_list, start_date, end_date)

        elif option == 'MARKET WEIGHTED':
            market_weighted(ticker_list, start_date, end_date)

        elif option == 'SMART WEIGHTED':
            smart_weighted(ticker_list, start_date, end_date)

        else:
            print('Invalid weight option.')


# Earnings per Share/ Return on equity?


# Company info (location, industry, market capitalization)
def company_info(ticker):
    location = ticker.info['city'] + ", " + ticker.info['country']
    industry = ticker.info['industry']
    market_cap = ticker.info['marketCap']
    return [location, industry, market_cap]
    ax2.set_ylabel('Monthly Portflio Returns')

    # Create png of graphs
    graphs_png = plt.savefig(f'{user_id}.png')

    return graphs_png


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

def pe_ratio(ticker_list):

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
    if ticker1['regularMarketPrice'] != None or ticker2['regularMarketPrice'] != None:
        ... #get monthly returns here 
    else:
        print("Invalid Ticker(s). Please try again.")

# Different companies and fees