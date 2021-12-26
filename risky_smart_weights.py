import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta, timezone
from threading import Thread
import random


def last_trading_day():
    rightnow = datetime.now(timezone(timedelta(hours=-5), 'EST'))

    # US Markets close at 4pm, but afterhours trading ends at 8pm.
    # yFinance stubbornly only gives the day's data after 8pm, so we will wait until 9pm to pull data from
    # the current day.
    market_close = rightnow.replace(hour=21, minute=0, second=0, microsecond=0)
    if rightnow < market_close:
        DELTA = 1
    # If it is saturday or sunday
    elif rightnow.weekday() >= 5:
        DELTA = 1
    else:
        DELTA = 0
        
    start_date = (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d")
    end_date = (datetime.now() - pd.tseries.offsets.BDay(DELTA)).strftime("%Y-%m-%d")
    MarketIndex = "^GSPC" # We can use the S&P 500's data to see the last day where we have data

    market_hist = yf.Ticker(MarketIndex).history(start=start_date, end=end_date).filter(like="Close").dropna()   

    latest_day = market_hist.index[-1]
    return latest_day.strftime("%Y-%m-%d")


# get_stock_beta produces the beta of a specified ticker
# Inputs:
# stock_returns_series is of type Series, represents the column of a dataframe of the returns of the price

def get_weight_list(k):
    # We will pick k random numbers from a range of 250 numbers
    # random.sample is O(n), so we want to minimize this number
    random_num_list = random.sample(range(250), k)
    
    listsum = sum(random_num_list)
    for i in range(len(random_num_list)):
        random_num_list[i] /= listsum
        
    return random_num_list
    
    
def get_stock_beta(stock_returns_series, marketVar, market_hist):
    binary_portfolio = market_hist[["Returns"]].copy()
    binary_portfolio["stock"] = stock_returns_series
    return (binary_portfolio.cov() / marketVar)['stock'].loc["Returns"]


#get_all_betas takes a list of tickers and outputs a list of all the betas of every
# ticker in the list.

def get_all_betas(ticker_list, ticker_hist, marketVar, market_hist):
    betas = {}
    for ticker in ticker_list:
        ticker_returns = ticker_hist[ticker][['Close']].pct_change()*100
        betas[ticker] = get_stock_beta(ticker_returns['Close'], marketVar, market_hist)
    return betas    


def get_option_interest(ticker):
    stock = yf.Ticker(ticker)
    options = stock.option_chain(stock.options[0])
    calls = pd.DataFrame().append(options.calls)
    puts = pd.DataFrame().append(options.puts)
    option_interest = calls.loc[calls['inTheMoney']]['openInterest'].sum() + puts.loc[puts['inTheMoney']]['openInterest'].sum()
    return option_interest   


def get_daily_volume(ticker, start, end, ticker_hist):
    filled_in_hist = ticker_hist.copy()
    filled_in_hist.fillna(0, inplace=True)
    volume = ticker_hist[ticker].loc[pd.to_datetime(start) : pd.to_datetime(end)].Volume.mean()
    return volume


def import_options(tickerlist, opt_start, opt_end, tickerhist):
    option_interest_dict = {}
    for ticker in tickerlist:
        try:
            open_interest = get_option_interest(ticker)
            daily_vol = get_daily_volume(ticker, opt_start, opt_end, tickerhist)
            option_interest_dict[ticker] = open_interest / daily_vol
        # yFinance's historical data is sometimes incomplete. This try except will catch any tickers that have insufficient data and drops them from our analysis.
        except IndexError as error:
            print(f'Dropped {ticker} - no data')   
    return option_interest_dict


def generate_risky_portfolio(tickerlist: list, totalspend: int):
    ticker_hist = yf.download(
                tickers = " ".join(tickerlist),
                # Download Data From the past 6 months
                period = "6mo",
                interval = "1d",
                group_by = 'ticker',
                threads = True,
            )
    
    # Data Cleanup
    ticker_hist.dropna(how='all', inplace=True)
    ticker_hist.fillna(method='ffill', inplace=True)
    ticker_hist.fillna(method='bfill', inplace=True)
    
    start_date = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
    end_date = last_trading_day()
    
    MarketIndex = "^GSPC" # We will compare each stock's covariance to the S&P 500

    market_hist = yf.Ticker(MarketIndex).history(start=start_date, end=end_date).filter(like="Close")
    market_hist["Returns"] = market_hist["Close"].pct_change()*100

    market_var = market_hist["Returns"].var()
    
    beta_dict = get_all_betas(tickerlist, ticker_hist, market_var, market_hist)
    beta_df = pd.DataFrame.from_dict(beta_dict, orient='index')
    beta_df.columns = ['Beta']
    beta_df.index.name = 'Ticker'
    
    #Sorts the dictionary from lowest beta to highest beta
    sorted_beta_df = beta_df.sort_values('Beta').copy()

    if len(sorted_beta_df) > 10:
        #Creates a dataframe with the 10 lowest betas and 10 highest betas.
        lower_bound = sorted_beta_df.iloc[:10]
        upper_bound = sorted_beta_df.iloc[-10:]
        # Gets the final stock list we want

        #Calculates the mean of the upper and lower list of betas
        avg_upper = upper_bound['Beta'].mean()
        avg_lower = lower_bound['Beta'].mean()

        # Compares the averages of the two and makes the one with the higher absolute value a 
        # candidate for our final list of stocks.
        if abs(avg_upper) >= abs(avg_lower):
            beta_final_ticker_list = list(upper_bound.index)
        else:
            beta_final_ticker_list = list(lower_bound.index)
    else:
        beta_final_ticker_list = list(sorted_beta_df.index)
    
    # Options Analysis
    
    opt_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    opt_end = end_date
    
    option_interest_dict = import_options(tickerlist, opt_start, opt_end, ticker_hist)
    
    if len(option_interest_dict.keys()) >= len(beta_final_ticker_list):
        # Creates a dataframe that corresponds tickers with the option interest over the daily volume
        option_interest_df = pd.DataFrame.from_dict(option_interest_dict, orient='index')
        option_interest_df.columns = ['Option Interest / dailyVol']
        sorted_option_interest_df = option_interest_df.sort_values('Option Interest / dailyVol').copy()
        sorted_option_interest_df.dropna(inplace=True)
        final_option_df = sorted_option_interest_df.tail(10)
        opt_tickers = list(final_option_df.index)
        print('Found an option portfolio')
    else:
        option_interest_df = False
        print('Error - Insufficient options data for inputted tickers, skipping options analysis...')
    
    # Monte Carlo Analysis
    trials = 10
    
    # We will collect the risk coefficients of all portfolios in this dictionary
    # Ultimately, we are comparing the best stocks obtained by the beta and options method,
    # and will take the best one from whichever method.
    risk_coefficients = {}
    
    # Don't mind the O(4n^2), it's O(e^2ln(2n)) :^)
    for i in range(trials):
        portfolio = pd.DataFrame(index=pd.date_range(start=start_date, end=end_date))
        portfolio_shares = {}
        weight_list = get_weight_list(len(beta_final_ticker_list))
        total = 0
        for i in range(len(beta_final_ticker_list)):
            allocation = weight_list[i] * totalspend
            # Simulate purchasing $100,000 worth of shares at the beginning of the time period
            initial_ticker_price = ticker_hist[beta_final_ticker_list[i]].Close.iloc[0]
            shares = allocation / initial_ticker_price
            
            # Alongside this, create a portfolio of shares with the same weightings, but priced in the present.
            present_ticker_price = ticker_hist[beta_final_ticker_list[i]].Close.loc[end_date]
            shares_present = allocation / present_ticker_price
            portfolio_shares[beta_final_ticker_list[i]] = shares_present
            total += present_ticker_price * shares_present
            
            # Simulate Purchasing of the shares and perform analysis on the past data
            portfolio[beta_final_ticker_list[i]] = shares * ticker_hist[beta_final_ticker_list[i]].loc[pd.to_datetime(start_date) : pd.to_datetime(end_date)].Close
        portfolio.dropna(how='all', inplace=True)
        portfolio.fillna(method='ffill', inplace=True)
        portfolio.fillna(method='bfill', inplace=True)
        portfolio['Total Value'] = portfolio.sum(axis=1)
        portfolio['Percent Return'] = portfolio['Total Value'].pct_change() * 100

        # Calculate risk coefficient
        std = portfolio['Percent Return'].std()
        avg_return = portfolio['Percent Return'].mean()
        risk_coefficient = (avg_return * std) ** 2
        
        # Save into risk_coefficients dict
        risk_coefficients[risk_coefficient] = portfolio_shares
        
        if option_interest_df is not False:
            portfolio = pd.DataFrame(index=pd.date_range(start=start_date, end=end_date))
            portfolio_shares = {}
            weight_list = get_weight_list(len(opt_tickers))
            total = 0
            for i in range(len(opt_tickers)):
                allocation = weight_list[i] * totalspend
                # Simulate purchasing $100,000 worth of shares at the beginning of the time period
                initial_ticker_price = ticker_hist[opt_tickers[i]].Close.iloc[0]
                shares = allocation / initial_ticker_price
                
                # Alongside this, create a portfolio of shares with the same weightings, but priced in the present.
                present_ticker_price = ticker_hist[opt_tickers[i]].Close.loc[end_date]
                shares_present = allocation / present_ticker_price
                portfolio_shares[opt_tickers[i]] = shares_present
                total += present_ticker_price * shares_present
                
                # Simulate Purchasing of the shares and perform analysis on the past data
                portfolio[opt_tickers[i]] = shares * ticker_hist[opt_tickers[i]].loc[pd.to_datetime(start_date) : pd.to_datetime(end_date)].Close
            portfolio.dropna(how='all', inplace=True)
            portfolio.fillna(method='ffill', inplace=True)
            portfolio.fillna(method='bfill', inplace=True)
            portfolio['Total Value'] = portfolio.sum(axis=1)
            portfolio['Percent Return'] = portfolio['Total Value'].pct_change() * 100

            # Calculate risk coefficient
            std = portfolio['Percent Return'].std()
            avg_return = portfolio['Percent Return'].mean()
            risk_coefficient = (avg_return * std) ** 2
            
            # Save into risk_coefficients dict
            risk_coefficients[risk_coefficient] = portfolio_shares
    
    optimal_weight = risk_coefficients[max(risk_coefficients.keys())]
    
    # Create final output portfolio
    final_stocks_df = pd.DataFrame.from_dict(optimal_weight, orient='index')
    final_stocks_df.reset_index(inplace=True)
    final_stocks_df.columns = ['Ticker', 'Shares']
    final_stocks_df.set_index('Ticker', inplace=True)
    return (final_stocks_df, end_date)