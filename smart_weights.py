import yfinance as yf
import matplotlib.pyplot as plt
import numpy as npf
import pandas as pd
import datetime 
from datetime import date
import random

from finance_functions import *

def smart_weighted(ticker_list, start_date, end_date, option, initial_capital):
    if option not in ('RISKY', 'SAFE'):
        return None
    elif option == 'RISKY':
        pass
    else:
        return generate_safe_portfolio(ticker_list, start_date, end_date, initial_capital)


def safe_method(ticker_list, start_date, end_date):  
    
    data = yf.download(ticker_list, start=start_date, end=end_date)
    data = data['Adj Close']
    
    #Calculate percent change
    percent_change = data.pct_change().apply(lambda x: npf.log(1 + x))

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
        lambda x: x * npf.sqrt(trading_days)
    )

    yearly_stats['Volatility'] = annual_std
    
    weights = []
    returns = []
    volatility = []

    for i in range (1000):
        individual_weights = npf.random.random(len(ticker_list))
        individual_weights = individual_weights/npf.sum(individual_weights)
        weights.append(individual_weights)

        individual_returns = npf.dot(individual_weights, yearly_stats.Returns)
        returns.append(individual_returns)

        portfolio_variance = (
            cov_matrix.mul(individual_weights, axis = 0)
            .mul(individual_weights, axis=1)
            .sum()
            .sum()
        )

        standard_deviation = npf.sqrt(portfolio_variance)
        individual_volatility = standard_deviation * npf.sqrt(trading_days)
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
    random_portfolios
    safest_portfolio = random_portfolios.iloc[random_portfolios.Volatility.idxmin()]

    pd.DataFrame(safest_portfolio)
    
    date = last_trading_day()
    
    current_day = datetime.strptime(date, "%Y-%m-%d")

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
            
    return FinalPortfolio