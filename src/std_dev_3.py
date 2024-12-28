import yfinance as yf
import numpy as np
from datetime import *
import pandas as pd

# Define the stock symbol and other variables
ticker = 'MSTR'
exp_date = date(2025,1,3)

# Fetch the historical data
stock_data = yf.download(ticker, period="1mo")

def standard_dev():
    # Calculate standard deviation of closing prices
    np_stdev = np.std(stock_data['Close'])
    #print('np std dev:', np_stdev)

    # Get the current stock price
    current_price = stock_data['Close'][-1]

    np_std = current_price - np_stdev

    # Define number of days for the price range
    today = date.today()
    days = float((exp_date - today).days)

    # Calculate the price range based on daily mean and standard deviation
    price_range = np_stdev * np.sqrt(days)

    # Calculate the upper and lower bounds
    upper_bound = stock_data["Close"].iloc[-1] + price_range
    lower_bound = stock_data["Close"].iloc[-1] - price_range
    mean = np.mean([upper_bound, lower_bound])
    
    return current_price, np_std, upper_bound, mean, lower_bound

def market_phase(current_price):
    ## Phases
    # Ease of use
    price = current_price
    fastavg = 50
    slowavg = 200

    fastsma = price/fastavg
    slowsma = price/slowavg

    print('fastavg:', fastavg)
    print('slowavg', slowavg)

    # Bullish criteria define below
    # Bullish Phase : close > 50 SMA, close > 200 SMA, 50 SMA > 200 SMA
    bullphase = fastsma > slowsma and price > fastsma and price > slowsma

    # Accumulation Phase : close > 50 SMA, close > 200 SMA, 50 SMA < 200 SMA
    accphase = fastsma < slowsma and price > fastsma and price > slowsma

    # Recovery Phase : close > 50 SMA, close < 200 SMA, 50 SMA < 200 SMA
    recphase = fastsma < slowsma and price < slowsma and price > fastsma

    # Bearish Criteria define below
    # Bearish Phase : close < 50 SMA, close < 200 SMA, 50 SMA < 200 SMA
    bearphase = fastsma < slowsma and price < fastsma and price < slowsma

    # Distribution Phase : close < 50 SMA, close < 200 SMA, 50 SMA > 200 SMA
    distphase = fastsma > slowsma and price < fastsma and price < slowsma

    # Warning Phase : close < 50 SMA, close > 200 SMA, 50 SMA > 200 SMA
    warnphase = fastsma > slowsma and price > slowsma and price < fastsma

    #print('bullphase', bullphase)
    #print('accphase', accphase)
    #print('recphase', recphase)
    #print('bearphase', bearphase)
    #print('distphase', distphase)
    #print('warnphase', warnphase)

    phase = ''

    if bullphase:
        phase = 'bullphase'
    if accphase:
        phase = 'accphase'    
    if recphase:
        phase = 'recphase'
    if bearphase:
        phase = 'bearphase'
    if distphase:
        phase = 'distphase'
    if warnphase:
        phase = 'warnphase'    

    return phase  

# Momentum Crossover
def calculate_momentum_crossover(data, short_window, long_window):
    """Calculates momentum crossover signals.

    Args:
        data (pd.DataFrame): DataFrame containing the price data.
        short_window (int): Window size for the short-term moving average.
        long_window (int): Window size for the long-term moving average.

    Returns:
        pd.DataFrame: DataFrame with the original data and a 'signal' column.
    """

    data['short_ma'] = data['price'].rolling(window=short_window).mean()
    data['long_ma'] = data['price'].rolling(window=long_window).mean()

    data['signal'] = 0
    data.loc[data['short_ma'] > data['long_ma'], 'signal'] = 1
    data.loc[data['short_ma'] < data['long_ma'], 'signal'] = -1

    return data

def calculate_price_direction(ticker, days=20):
    """Calculates the price direction of a stock over the past 'days'."""

    # Fetch historical data using yfinance
    data = yf.download(ticker, period=f"{days}d")

    # Calculate the price change
    price_change = data['Close'][-1] - data['Close'][0]

    if price_change > 0:
        return "Up"
    elif price_change < 0:
        return "Down"
    else:
        return "Flat"
    

# Stardard Deviation  
current_price, np_std, upper_bound, mean, lower_bound = standard_dev()

# this looks right
#print(f"Standard Deviation with statistics: {tos_std:.2f}")
print(f"Standard Deviation with np: {np_std:.2f}")
print(f"Current Price: {current_price:.2f}")

# print(f"Predicted price range for {days} day using np:")
print(f"Upper bound: {upper_bound:.2f}")
print(f"Mean: {mean:.2f}")
print(f"Lower bound: {lower_bound:.2f}")  

# Market Phase
mkt_phase = market_phase(current_price)   
print(mkt_phase) 

# Momemtum Crossover:
int_stock_data = stock_data['Close'].astype(int)
prices_list = int_stock_data.values.tolist()
df_prices = pd.DataFrame({'price': prices_list})
data = calculate_momentum_crossover(df_prices, 3, 5)

# Last row is the most current signal
# Get the last row
last_row = df_prices.iloc[-1]

# Get the value in the last column of the last row
last_row_last_column_value = last_row.iloc[-1]

signal = ''
if last_row_last_column_value == -1:
    signal = 'Sell'
else:
    signal = 'Buy'

print('Buy/Sell Signal:', signal )

# Price Direction
direction = calculate_price_direction(ticker)
print(f"The price direction of {ticker} over the past 20 days is: {direction}")
