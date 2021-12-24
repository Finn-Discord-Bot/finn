import yfinance as yf
import matplotlib.pyplot as plt
import numpy as npf
import pandas as pd
import datetime 
from datetime import date


def market_weighted(ticker_list, start_date, end_date):
    
    length = len(ticker_list)
    close_df = pd.DataFrame()
    ticker_obj = {}
    sharesOut = {}
    for i in range(length):
        ticker_obj[i] = yf.Ticker(ticker_list[i])
        sharesOut[i] = ticker_obj[i].info['sharesOutstanding']
        close_df["Close{0}".format(i)] = ticker_obj[i].history(start = start_date, end = end_date).Close

    
    return close_df
df = market_weighted(['AAPL', 'GOOG'], '2021-01-01', '2021-12-01')
print(df.iat[0,0])