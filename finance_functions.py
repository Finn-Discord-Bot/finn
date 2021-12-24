import yfinance as yf
import matplotlib
import numpy as npf
import pandas as pd
import datetime 
from datetime import date


# Variables





# Stock Info (Open, High, Low, Close, Volume, Dividends, Stock Splits)

def stock_info(ticker):
    global stock 
    global stock_info
    stock = yf.Ticker(ticker)
    stock_info = stock.info
    


def stock_info(ticker):
    stock_open = stock_info["open"]
    stock_close = stock_info["close"]
    print(stock_open)
stock_info("AAPL")

# PyZipFile Class for creating ZIP archives containing Python libraries.     class zipfile.ZipInfo(filename='NoName', date_time=, 1980, 1, 1, 0, 0, 0)
# Stock History 

def stock_history(ticker, start_date, end_date):
    current_date = date.today()
    if start_date = "" or end_date = "":
        stock_history = stock.history(start = date.today, end = date.today) 
    else:
        stock_history = stock.history(start = start_date, end = end_date) 

# Earnings per Share:


# Company info (location, industry, market capitalization, )
def comapny_info(ticker):
    
    

# Stock options (aka if the company offers common or preferred shares)


# Dividend yields


# P/E Ratios
def pe_ratio():
    ...

# Trends (downwards, upwards, consumes a time interval and will give the % change in that time period)
def trends(time_period):
    ...

# The graphs (daily, monthly returns, expected returns ?)
def portfolio_graphs(portfolio):

    fig, ((ax1), (ax2))
    # Daily returns
    plt.figure(figsize=(20,15))
    plt.plot(portfolio.index, portfolio['Daily Returns'], colour='r')
    


    # Monthly retuns
    plt.plot(portfolio.index, portfolio['Monthly Returns'], colour='b')
    monthly_exp_mr = 

# Beta Value
def beta(stock):
    market_index = yf.Ticker('^GSPC')

# Sharpe Ratio
def sharpe_ratio(stock):
    ...

# Options
def options(stock):
    ... 

#Volatility (standard deviation)
def std(portfolio):
    ... 


#Correlation with other stocks (need 2 tickers to be inputed)
def correlation(stock1, stock2):
    ...

# Different companies and fees