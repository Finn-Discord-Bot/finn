import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime 
from datetime import timedelta, timezone

from risky_smart_weights import generate_risky_portfolio


def last_trading_day():
    now = datetime.datetime.now(timezone(timedelta(hours=-5), 'EST'))

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
        
    start_date = (datetime.datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d")
    end_date = (datetime.datetime.now() - pd.tseries.offsets.BDay(DELTA)).strftime("%Y-%m-%d")
    MarketIndex = "^GSPC" # We can use the S&P 500's data to see the last day where we have data

    market_hist = yf.Ticker(MarketIndex).history(start=start_date, end=end_date).filter(like="Close").dropna()   

    latest_day = market_hist.index[-1]
    return latest_day.strftime("%Y-%m-%d")


def smart_weighted(ticker_list, option, initial_capital):
    if option not in ('RISKY', 'SAFE'):
        return None
    elif option == 'RISKY':
        return generate_risky_portfolio(ticker_list, initial_capital)
    else:
        start_date = (datetime.datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
        end_date = last_trading_day()
        return generate_safe_portfolio(ticker_list, start_date, end_date, initial_capital)


def safe_method(ticker_list, start_date, end_date):  
    
    data = yf.download(ticker_list, start=start_date, end=end_date)
    data = data['Adj Close']
    
    #Calculate percent change
    percent_change = data.pct_change().apply(lambda x: np.log(1 + x))

    #Caluclate covariance
    cov_matrix = percent_change.cov()

    #Calculate STD
    corr_matrix = percent_change.corr()

    #Caluclate Yearly Expected Returns
    data.index = pd.to_datetime(data.index)

    ind_expected_returns = data.resample('Y').first().pct_change().mean()
    
    yearly_stats = pd.DataFrame(ind_expected_returns, columns=['Returns'])

    trading_days = 250

    #Calculate annual std
    annual_std = percent_change.std().apply(
        lambda x: x * np.sqrt(trading_days)
    )

    yearly_stats['Volatility'] = annual_std
    
    weights = []
    returns = []
    volatility = []

    for i in range(10):
        individual_weights = np.random.random(len(ticker_list))
        individual_weights = individual_weights/np.sum(individual_weights)
        weights.append(individual_weights)

        individual_returns = np.dot(individual_weights, yearly_stats.Returns)
        returns.append(individual_returns)

        portfolio_variance = (
            cov_matrix.mul(individual_weights, axis = 0)
            .mul(individual_weights, axis=1)
            .sum()
            .sum()
        )

        standard_deviation = np.sqrt(portfolio_variance)
        individual_volatility = standard_deviation * np.sqrt(trading_days)
        volatility.append(individual_volatility)
    
    portfolios = pd.DataFrame(index=range(1000))
    portfolios['Returns'] = returns
    portfolios['Volatility'] = volatility

    for i in range (len(ticker_list)):
        for j in range (1000):
            portfolios[ticker_list[i]] = weights[j][i]
    
    return portfolios

def generate_safe_portfolio(ticker_list, start_date, end_date, initial_capital):
    random_portfolios = safe_method(ticker_list, start_date, end_date)
    safest_portfolio = random_portfolios.iloc[random_portfolios.Volatility.idxmin()]

    pd.DataFrame(safest_portfolio)
    
    date = last_trading_day()
    
    current_day = datetime.datetime.strptime(date, "%Y-%m-%d")

    next_day = current_day + timedelta(days=1)

    final_portfolio_columns = ["Ticker", "Price", "Shares", "Value", "Weight"]

    FinalPortfolio = pd.DataFrame(columns=final_portfolio_columns)

    safest_portfolio_data = safest_portfolio[2:]

    safest_portfolio_data = safest_portfolio_data.sort_index()

    safest_portfolio_tickers = list(safest_portfolio_data.index)

    safest_portfolio_weights = list(safest_portfolio_data.values)

    prices = yf.download(safest_portfolio_tickers, start=current_day, end=next_day)
    
    current_prices = prices["Adj Close"].loc[date]

    FinalPortfolio['Ticker'] = safest_portfolio_tickers

    FinalPortfolio['Price'] = current_prices.values

    FinalPortfolio['Weight'] = safest_portfolio_weights

    FinalPortfolio['Value'] = initial_capital * FinalPortfolio.Weight

    FinalPortfolio['Shares'] = FinalPortfolio.Value / FinalPortfolio.Price

    FinalPortfolio = FinalPortfolio[['Ticker', 'Shares']]
    
    FinalPortfolio.set_index('Ticker', inplace=True)
            
    return (FinalPortfolio, current_day)