import yfinance as yf
import matplotlib.pyplot as plt
import numpy as npf
import pandas as pd
import datetime 
from datetime import date, datetime, timedelta, timezone

#from finance_functions import *


def valid_ticker_list(ticker_list):
    ticker_hist = yf.download(
                    tickers = " ".join(ticker_list),
                    # Download Data From the past 6 months
                    period = "5d",
                    interval = "1d",
                    group_by = 'tickers',
                    threads = True
                )
    return list(dict.fromkeys([t[0] for t in ticker_hist.dropna(axis=1, how='all').columns]))
# def valid_ticker_list(ticker_list):
#     new_ticker_list = []
#     for x in ticker_list:
#         ticker = yf.Ticker(x)
#         info = None
        
#         try:
#             info = ticker.info
#             new_ticker_list.append(ticker)
#         except:
#             pass
#     return new_ticker_list
            
        


def create_price_list(ticker_list):
    new_ticker_list = sorted(ticker_list)
    price_list = []
    ticker_hist = yf.download(
                    tickers = " ".join(ticker_list),
                    # Download Data From the past 6 months
                    period = "5d",
                    interval = "1d",
                   # group_by = 'tickers',
                    threads = True
                )
    last_row = ticker_hist['Close'].iloc[-1]
    last_date = ticker_hist.iloc[-1]
    for x in new_ticker_list:
        price_list.append(last_row[x])
    return (price_list, last_date.name)




def price_weighted(starting_balance, ticker_list, price_list):

    # Create DataFrame
    pw_portfolio = pd.DataFrame(index = ticker_list)
    pw_portfolio["Shares"] = 0
    num_tickers = len(ticker_list)
    value_per_share = starting_balance/num_tickers
    
    # Add Close price columns for each stock
    
    for i in range(len(ticker_list)):
        
        pw_portfolio['Shares'].loc[ticker_list[i]] = value_per_share/price_list[i]
    

    return pw_portfolio


def market_weighted(ticker_list, starting_balance, price_list):
    
    stock_dict = {}
    totalMarketCap = 0
    for i in range(len(ticker_list)):
        info = yf.Ticker(ticker_list[i]).info
        stock_dict[f"{ticker_list[i]} Shares Outstanding"] = info["sharesOutstanding"]
        stock_dict[f"{ticker_list[i]} Market Capitalization"] = stock_dict[f"{ticker_list[i]} Shares Outstanding"] * price_list[i]
        totalMarketCap += stock_dict[f"{ticker_list[i]} Market Capitalization"]
    
    #ticker_list = ["AAPL", "GOOG", "TSLA"]
    market_weighted_df = pd.DataFrame(index = ticker_list)
    market_weighted_df.index.rename("Ticker", inplace = True)
    market_weighted_df["Shares"] = 0
    
    for i in range(len(ticker_list)):
        stock_dict[f"{ticker_list[i]} Market Capitalization Percent"] = stock_dict[f"{ticker_list[i]} Market Capitalization"] / totalMarketCap
        #print(stock_dict[f"{ticker} Market Capitalization Percent"])
        #print(stock_dict[f"{ticker} Market Capitalization Percent"] * starting_balance)
        market_weighted_df.loc[ticker_list[i],"Shares"] = (stock_dict[f"{ticker_list[i]} Market Capitalization Percent"] * starting_balance) / price_list[i]
   
    return market_weighted_df

    
#print(market_weighted(tick_list,10000, priced_list))

#good
def portfolio_maker(ticker_list, weight_option, investment):
    
    # Get valid ticker list
    valid_tickers = valid_ticker_list(ticker_list)

    if not valid_tickers:
        print('No valid tickers were inputted!')
        return None
    elif len(valid_tickers) > 10:
        print('Exceeded Maximum Number of Tickers!')
        return None
    else:
        # check weight option
        if weight_option == 'PRICE WEIGHTED':
            portfolio = price_weighted(ticker_list)

        elif weight_option == 'MARKET WEIGHTED':
            portfolio = market_weighted(ticker_list)

        else:
            portfolio = smart_weighted(ticker_list, weight_option)
        
        if not portfolio:
            return None
        else:
            pass
        return True

print(yf.Ticker("TSLA").info["sharesOutstanding"])