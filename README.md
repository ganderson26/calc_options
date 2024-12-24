# Project Title

calc_options

## Description

Gather Option Data for the contract.

## Getting Started

### For Local Development

#### Dependencies

* Install MySQL
* Install Python packages

#### Installing

* Install MySQL 8.0.40, create the Database and Table
* Install Python packages
```
pip install flask yahoo_fin numpy scipy pandas datetime mysql-connector-python Flask.Response
```

#### Executing program

* How to run the program
* Step-by-step
* For Development on Local, add an environment variable named LOCAL and set to LOCAL. I did this in ~/.bash_profile
* The variable is used in options_flask.py to set the MySQL connection to use the local instance of the database and set all URLs to the local instance of the application. When deployed to GoDaddy, you will need to create the environment variable and set to GODADDY in order to use their server.
```
# Set environment variable for Python apps
export LOCAL="LOCAL"
```

* cd to src folder
* * Then run the flask command
```
flask --app options_flask --debug run
```

 * You should see:
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
 * Open and browser and go the address

![alt text](image.png)

* Exit from the terminal/bash
```
ctrl-c
```


#### For GoDaddy Deployment and running



#### Dependencies

* Create MySQL Database and Table
* Create a Python Application
* Create environment variable 
* Install Python packages
* Upload application
* Run

#### Create MySQL Database and Table

* Log into GoDaddy, select your Domain and go to cPanel
* Select MySQL Databases
* Create the Database and Table

#### Create a Python Application

* Log into GoDaddy, select your Domain and go to cPanel
* Create a Python Application

![alt text](image-1.png)

#### Create environment variable

* Scroll down and create the environment variable 

![alt text](image-2.png)


#### Installing Packages

* From your local terminal/bash, SSH into the GoDaddy server
* You will need to get the server address
* And add SSH
```
$ssh jejtxlk4zmlg@50.63.7.156
jejtxlk4zmlg@50.63.7.156's password: ************
jejtxlk4zmlg@p3plzcpnl505185 [~]$ 
```

* Change directory to the directory created by GoDaddy
```
source /home/jejtxlk4zmlg/virtualenv/options/3.9/bin/activate && cd /home/jejtxlk4zmlg/options
```

* Install Python packages
```
pip install flask yahoo_fin numpy scipy pandas datetime mysql-connector-python Flask.Response
```

#### Upload your Application

* I used FileZilla to create the folder structure and upload the application

![alt text](image-3.png)

#### Executing program

* On the cPanel Application, click Run or Restart
* Click Open





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

* 0.2.0
    * Set connection variables based on environment variable LOCAL
    * Export transactions to CSV
    * Disable/Enable View Edit button on transactions.html
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
