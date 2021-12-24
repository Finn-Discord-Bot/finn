import yfinance as yf
import matplotlib.pyplot as plt
import numpy as npf
import pandas as pd
import datetime 
from datetime import date, datetime, timedelta, timezone


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

    market_hist = yf.Ticker(MarketIndex).history(start=start_date, end=end_date).filter(like="Close")   

    latest_day = market_hist.index[-1]
    return latest_day.strftime("%Y-%m-%d")

print(last_trading_day())

# def market_weighted(ticker_list, start_date, end_date):
    
#     length = len(ticker_list)
#     close_df = pd.DataFrame()
#     ticker_obj = {}
#     sharesOut = {}
#     for i in range(length):
#         ticker_obj[i] = yf.Ticker(ticker_list[i])
#         sharesOut[i] = ticker_obj[i].info['sharesOutstanding']
#         close_df["Close{0}".format(i)] = ticker_obj[i].history(start = start_date, end = end_date).Close

    
#     return close_df
# df = market_weighted(['AAPL', 'GOOG'], '2021-01-01', '2021-12-01')
# print(df.iat[0,0])