import yfinance as yf
import matplotlib.pyplot as plt
import numpy as npf
import pandas as pd
import datetime 
from datetime import date, datetime, timedelta, timezone

from finance_functions import *
print(testFunc("AAPL"))

ticker_hist = yf.download(
                    tickers = " ".join(['AAPL', '^GSPC']),
                    # Download Data From the past 6 months
                    period = "6mo",
                    interval = "1d",
                    group_by = 'tickers',
                    threads = True
                )
ticker_hist['AAPL']