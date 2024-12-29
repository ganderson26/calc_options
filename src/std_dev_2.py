# https://medium.datadriveninvestor.com/using-standard-deviation-to-calculate-expected-stock-price-range-7e6baf2e32c9

import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np

data = yf.download("MSTR", period='7d')  # 1mo 7d
#print(data)

# We set the ‘ddof’ parameter to 1. It stands for “delta degrees of freedom.” It is used to adjust the calculation of the standard deviation to account for the sample size.
daily_std_dev = data['Close'].std(ddof=1)
print(daily_std_dev)
daily_mean = data["Close"].mean()
print(daily_mean)

'''
plt.figure(figsize=(12, 8))
plt.plot(data.index, data["Close"])
plt.axhline(y=daily_mean, color="k", linestyle="--", label="Mean")
#plt.axhline(y=std_1_upper, color="r", alpha=0.3, linestyle="-.", label="1 Std Dev")
#plt.axhline(y=std_1_lower, color="r", alpha=0.3, linestyle="-.")
#plt.axhline(y=std_2_upper, color="g", alpha=0.3, linestyle="-.", label="2 Std Dev")
##plt.axhline(y=std_2_lower, color="g", alpha=0.3, linestyle="-.")
#plt.fill_between(data.index, std_1_upper, std_1_lower, color="r", alpha=0.1)
#plt.fill_between(data.index, std_2_upper, std_2_lower, color="g", alpha=0.1)
plt.legend()
plt.title("MSTR Prices with Standard Deviation Levels")
plt.ylabel("Daily Return")
plt.xlabel("Date")
plt.show()
'''


# Define number of days for the price range
days = 7


# Calculate the price range based on daily mean and standard deviation
price_range = daily_std_dev * np.sqrt(days)
print(price_range)

# Calculate the upper and lower bounds
upper_bound = data["Close"].iloc[-1] + price_range
lower_bound = data["Close"].iloc[-1] - price_range

#print the results 

print(f"Predicted price range for {days} day:")
print(f"Upper bound: {upper_bound:.2f}")
print(f"Lower bound: {lower_bound:.2f}")