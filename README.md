# Project Title

calc_options

## Description

Gather Option Data for the contract.

## Getting Started

### Dependencies

* Install MySQL
* Install Python packages

### Installing


* Install MySQL 8.0.40
* Install Python packages
```
pip install flask yahoo_fin numpy scipy pandas datetime mysql-connector-python
```

### Executing program

* How to run the program
* Step-by-step
* For Development on Local, comment out godaddy and uncomment local variables
```
# Set for local or godaddy
##mysql_user = "jejtxlk4zmlg" # godaddy
mysql_user = "root" # local

##view_login = "http://26miles.com/options/login"  # godaddy
view_login = "http://127.0.0.1:5000/login"  # local

##view_home = "http://26miles.com/options/" # godaddy
view_home = "http://127.0.0.1:5000/" # local

##send_transaction_to_edit = "http://26miles.com/options/send_transaction" # godaddy
send_transaction_to_edit = "http://127.0.0.1:5000/send_transaction" # local

##edit_transaction_to_edit = "http://26miles.com/options/edit_transaction" # godaddy
edit_transaction_to_edit = "http://127.0.0.1:5000/edit_transaction" # local

##view_index = "http://26miles.com/options/index" # godaddy
view_index = "http://127.0.0.1:5000/index" # local

##view_option = "http://26miles.com/options/option" # godaddy
view_option = "http://127.0.0.1:5000/option" # local

##view_transactions = "http://26miles.com/options/transactions" # godaddy
view_transactions = "http://127.0.0.1:5000/transactions" # local

```
* cd to src folder
```
flask --app options_flask --debug run
```

* Then run the flask command and you should see:
```
 * Serving Flask app 'options_flask'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Restarting with watchdog (fsevents)
 * Debugger is active!
 * Debugger PIN: 427-590-107
```

![alt text](image.png)

* Exit
```
ctrl-c
```

## Help

* If you get the following error:
```
mysql.connector.errors.NotSupportedError: Authentication plugin 'caching_sha2_password' is not supported
```
* Try:
```
pip uninstall mysql-connector-python
pip install mysql-connector-python
```

## Authors

Max Glenn Anderson

## Version History

* 0.1.0
    * Initial Release

## License

* [LICENSE](LICENSE)

## Acknowledgments

Inspiration, code snippets, etc.
* [Flask](https://flask.palletsprojects.com/en/stable/)
* From ChatGPT
```
import numpy as np
from scipy.stats import norm

def black_scholes_delta(S, K, T, r, sigma, option_type='call'):
    """Calculates the delta of a call or put option using the Black-Scholes model."""

    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

    if option_type == 'call':
        delta = norm.cdf(d1)
    else:  # put option
        delta = -norm.cdf(-d1)

    return delta

# Example usage:
S = 100  # Current stock price
K = 105  # Strike price
T = 30 / 365  # Time to expiration (in years)
r = 0.05  # Risk-free interest rate
sigma = 0.2  # Volatility

delta = black_scholes_delta(S, K, T, r, sigma, 'call')
print(f"Delta of the call option: {delta:.4f}")
```
