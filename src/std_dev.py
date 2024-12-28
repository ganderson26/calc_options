import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import yfinance as yf

# Fetch historical data
start_date = dt.datetime(2020, 1, 1)
end_date = dt.datetime.now()
ticker = "MSTR"

#data = pdr.get_data_yahoo(ticker, start_date, end_date)
# Fetch the historical data
data = yf.download(ticker, start_date, end_date)

# Calculate daily returns
data['Returns'] = data['Adj Close'].pct_change()

# Calculate annualized volatility
volatility = data['Returns'].std() * np.sqrt(252)

# Monte Carlo simulation
num_simulations = 1000
num_days = 252  # One year of trading days

simulated_prices = []

for i in range(num_simulations):
    daily_returns = np.random.normal(0, volatility / np.sqrt(252), num_days)
    price_series = [data['Adj Close'][-1]]  # Start with last known price

    for j in daily_returns:
        price_series.append(price_series[-1] * (1 + j))

    simulated_prices.append(price_series)

# Calculate standard deviation of future prices
future_prices = np.array(simulated_prices)[:, -1]
future_std_dev = np.std(future_prices)

print(future_prices)

print("Estimated future standard deviation:", future_std_dev)

# Visualize simulations
plt.plot(simulated_prices)
plt.xlabel("Days")
plt.ylabel("Stock Price")
plt.title(f"Monte Carlo Simulation for {ticker}")
plt.show()
