# options_flask.py

from flask import Flask, render_template, redirect, url_for, request, Response, session
from yahoo_fin import options
from yahoo_fin import stock_info as si
from datetime import *
from urllib.parse import unquote
from werkzeug.security import generate_password_hash, check_password_hash
from scipy.stats import norm

import numpy as np
import pandas as pd
import mysql.connector
import yfinance as yf
import statistics
import re
import os
import logging

# Get environment variable and set variables based on running locally or on GoDaddy
value = os.getenv('LOCAL')
print(value)

if value == "LOCAL":
    mysql_user = "root" 
    view_home = "http://127.0.0.1:5000/index" 
    create_option = "http://127.0.0.1:5000/createoption" 
    send_transaction_to_edit = "http://127.0.0.1:5000/send_transaction"
    edit_transaction_to_edit = "http://127.0.0.1:5000/edit_transaction"
    view_index = "http://127.0.0.1:5000/index"
    view_option = "http://127.0.0.1:5000/option"
    view_transactions = "http://127.0.0.1:5000/transactions"
    view_login = "http://127.0.0.1:5000/login"
    send_logout = "http://127.0.0.1:5000/logout"
    send_register = "http://127.0.0.1:5000/register"
else:
    mysql_user = "jejtxlk4zmlg" 
    view_home = "http://26miles.com/options/index"    
    create_option = "http://26miles.com/options/createoption" 
    send_transaction_to_edit = "http://26miles.com/options/send_transaction" 
    edit_transaction_to_edit = "http://26miles.com/options/edit_transaction" 
    view_index = "http://26miles.com/options/index" 
    view_option = "http://26miles.com/options/option"
    view_transactions = "http://26miles.com/options/transactions" 
    view_login = "http://26miles.com/options/login"  
    send_logout = "http://26miles.com/options/logout" 
    send_register = "http://26miles.com/options/register"



# Functions   
def get_connection():
    # MySQL Connection
    mydb = mysql.connector.connect(
    host="localhost",
    user=mysql_user,
    password="Marathon#262",
    database="OPTIONS"
    )

    return mydb

def show_mysql_variables():
    mydb = get_connection()

    mycursor = mydb.cursor()

    mycursor.execute("SHOW VARIABLES")

    app.logger.error("MySQL Variables:")
    for x in mycursor:
        app.logger.error(x)

    mycursor.close()
    mydb.close()

def black_scholes_delta(S, K, T, r, sigma, option_type='call'):
    """Calculate the Black-Scholes delta for a call or put option.
    
    Args:
        S: Underlying asset price
        K: Strike price
        T: Time to maturity (in years)
        r: Risk-free interest rate
        sigma: Volatility:
        option_type: call or put.

    Returns:
        delta
    """

    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    
    if option_type == 'call':
        delta = norm.cdf(d1)
    else:
        delta = norm.cdf(d1) - 1

    delta = delta[~np.isnan(delta)]    

    return delta

def standard_dev(stock_data, exp_date):
    """Calculate standard deviation of closing prices.
    
    Args:
        stock_data: DataFrame of stock information
        exp_date: Expiration date

    Returns:
        current_price, np_std, upper_bound, mean, lower_bound
    """
    app.logger.error("In standard_dev()")

    np_stdev = np.std(stock_data['Close'])
   

    # Get the current stock price
    app.logger.error("In standard_dev() getting current_price")
    current_price = stock_data['Close'].iloc[-1]

    app.logger.error("In standard_dev() current_price:", current_price)


    np_std = current_price - np_stdev

    # Define number of days for the price range
    today = date.today()
    days = float((exp_date - today).days)

    # Calculate the price range based on daily mean and standard deviation
    price_range = np_stdev * np.sqrt(days)
    print(price_range)

    # Calculate the upper and lower bounds
    upper_bound = stock_data["Close"].iloc[-1] + price_range
    lower_bound = stock_data["Close"].iloc[-1] - price_range
    mean = np.mean([upper_bound, lower_bound])

    app.logger.error("In standard_dev() return")
    
    return current_price, np_std, upper_bound, mean, lower_bound

def market_phase(current_price):   
    """Calculate market phase.
    
    Args:
        current_price: Current price of stock

    Returns:
        phase
    """
    app.logger.error("In market phase")
    price = current_price
    fastavg = 50
    slowavg = 200

    fastsma = price/fastavg
    slowsma = price/slowavg

    # Bullish criteria define below
    # Bullish Phase : close > 50 SMA, close > 200 SMA, 50 SMA > 200 SMA
    #bullphase = ((fastsma > slowsma) & (price > fastsma)) & (price > slowsma)

    # Accumulation Phase : close > 50 SMA, close > 200 SMA, 50 SMA < 200 SMA
    #accphase = ((fastsma < slowsma) & (price > fastsma)) & (price > slowsma)

    # Recovery Phase : close > 50 SMA, close < 200 SMA, 50 SMA < 200 SMA
    #recphase = ((fastsma < slowsma) & (price < slowsma)) & (price > fastsma)

    # Bearish Criteria define below
    # Bearish Phase : close < 50 SMA, close < 200 SMA, 50 SMA < 200 SMA
    #bearphase = ((fastsma < slowsma) & (price < fastsma)) & (price < slowsma)

    # Distribution Phase : close < 50 SMA, close < 200 SMA, 50 SMA > 200 SMA
    #distphase = ((fastsma > slowsma) & (price < fastsma)) & (price < slowsma)

    # Warning Phase : close < 50 SMA, close > 200 SMA, 50 SMA > 200 SMA
    #warnphase = ((fastsma > slowsma) & (price > slowsma)) & (price < fastsma)

    phase = 'Unknown'

    #if bullphase:
    #    phase = 'bullphase'
    #if accphase:
    #    phase = 'accphase'    
    #if recphase:
    #    phase = 'recphase'
    #if bearphase:
    #    phase = 'bearphase'
    #if distphase:
    #    phase = 'distphase'
    #if warnphase:
    #    phase = 'warnphase' 
     
    # # Bullish criteria define below
    # Bullish Phase : close > 50 SMA, close > 200 SMA, 50 SMA > 200 SMA
    if (fastsma > slowsma).all() & (price > fastsma).all() & (price > slowsma).all():
        phase = 'Bull'

    # Accumulation Phase : close > 50 SMA, close > 200 SMA, 50 SMA < 200 SMA
    if  (fastsma < slowsma).all() & (price > fastsma).all() & (price > slowsma).all():
        phase = 'Accumulation'

    # Recovery Phase : close > 50 SMA, close < 200 SMA, 50 SMA < 200 SMA
    if (fastsma < slowsma).all() & (price < slowsma).all() & (price > fastsma).all():
        phase = 'Recovery'

    # Bearish Criteria define below
    # Bearish Phase : close < 50 SMA, close < 200 SMA, 50 SMA < 200 SMA
    if (fastsma < slowsma).all() & (price < fastsma).all() & (price < slowsma).all():
        phase = 'Bear'

    # Distribution Phase : close < 50 SMA, close < 200 SMA, 50 SMA > 200 SMA
    if (fastsma > slowsma).all() & (price < fastsma).all() & (price < slowsma).all():
        phase = 'Distribution'

    # Warning Phase : close < 50 SMA, close > 200 SMA, 50 SMA > 200 SMA
    if (fastsma > slowsma).all() & (price > slowsma).all() & (price < fastsma).all():
        phase = 'Warning'

    return phase  

def calculate_momentum_crossover(data, short_window, long_window):
    """Calculates momentum crossover signals.

    Args:
        data (pd.DataFrame): DataFrame containing the price data.
        short_window (int): Window size for the short-term moving average.
        long_window (int): Window size for the long-term moving average.

    Returns:
        pd.DataFrame: DataFrame with the original data and a 'signal' column.
    """
    app.logger.error("In momemtum crossover")

    app.logger.error("In momemtum crossover get short_ma and long_ma:")
    #df['column_name'] = pd.to_numeric(df['column_name'], errors='coerce')
    # data['short_ma'] = data['price'].rolling(window=short_window).mean()
    # data['long_ma'] = data['price'].rolling(window=long_window).mean()

    data['short_ma'] = pd.to_numeric(data['price'], errors='coerce').rolling(window=short_window).mean()
    data['long_ma'] = pd.to_numeric(data['price'], errors='coerce').rolling(window=long_window).mean()

    app.logger.error("In momemtum crossover getting signal")

    data['signal'] = 0
    data.loc[data['short_ma'] > data['long_ma'], 'signal'] = 1
    data.loc[data['short_ma'] < data['long_ma'], 'signal'] = -1

    return data

def calculate_price_direction(ticker):
    """Calculates the price direction of a stock over the past."""
    app.logger.error("In calculate price direction")

    # Fetch historical data using yfinance
    data = yf.download(ticker, period='1mo')

    # Calculate the price change
    price_change = data['Close'].iloc[-1] - data['Close'].iloc[0]

    app.logger.error("In calculate price direction check price")
    # The truth value of a Series is ambiguous. Use a.empty, a.bool(), a.item(), a.any() or a.all().
    if (price_change > 0).all():
        return "Up"
    elif (price_change < 0).all():
        return "Down"
    else:
        return "Flat"
    

# Create Flask app and set secret key for session variables
app = Flask(__name__)
app.secret_key = 'marathon'

app.logger.setLevel(logging.ERROR)

# Test Log levels
app.logger.debug("debug log info")
app.logger.info("Info log information")
app.logger.warning("Warning log info")
app.logger.error("Error log info")
app.logger.critical("Critical log info")

#app.logger.error("app.config['PERMANENT_SESSION_LIFETIME']:", app.config['PERMANENT_SESSION_LIFETIME'])
#app.logger.error("app.config['SESSION_PERMANENT']:", app.config['SESSION_PERMANENT'])

# Print all config values
#app.logger.error("All app.config values:")
#for key, value in app.config.items():
#    app.logger.error(f"{key}: {value}")
#app.logger.error("Error log info")

# Print MySQL Variables
##show_mysql_variables()  

# Routes
@app.route('/')
def start():
    return render_template('login.html', view_login=view_login, send_register=send_register)

@app.route('/login', methods =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'user_name' in request.form and 'password' in request.form:
        user_name = request.form['user_name']
        password = request.form['password']

        sql = "SELECT ID, USER_NAME, PASSWORD, EMAIL FROM OPTIONS.ACCOUNT WHERE USER_NAME = '" + user_name + "'"
        #values = (user_name)

        mydb = get_connection()

        mycursor = mydb.cursor()

        mycursor.execute(sql)
        
        account = mycursor.fetchone()

        if check_password_hash(account[2], password):
            if account:
                session['loggedin'] = True
                session['id'] = account[0]
                session['user_name'] = account[1]
                msg = 'Logged in successfully!'
                return render_template('index.html', msg=msg, view_index=view_index, view_option=view_option, view_transactions=view_transactions, send_logout=send_logout)
        else:
            msg = 'Incorrect user_name / password!'

        mycursor.close()
        mydb.close()    

    return render_template('login.html', msg = msg, view_login=view_login, send_register=send_register)
 
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('user_name', None)

    return render_template('login.html', view_login=view_login, send_register=send_register)
 
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'user_name' in request.form and 'password' in request.form and 'email' in request.form :
        user_name = request.form['user_name']
        password = request.form['password']
        email = request.form['email']
        hash_password = generate_password_hash(password)
        
        sql = "SELECT * FROM OPTIONS.ACCOUNT WHERE USER_NAME = '" + user_name + "'"
        values = (user_name)

        mydb = get_connection()
        
        mycursor = mydb.cursor()

        mycursor.execute(sql)

        account = mycursor.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', user_name):
            msg = 'Username must contain only characters and numbers!'
        elif not user_name or not password or not email:
            msg = 'Please fill out the form!'
        else:
            sql = 'INSERT INTO OPTIONS.ACCOUNT (USER_NAME, PASSWORD, EMAIL) VALUES (%s, %s, %s)'
            values = (user_name, hash_password, email)

            mycursor = mydb.cursor()

            mycursor.execute(sql, values)

            mydb.commit()

            mycursor.close()
            mydb.close()    

            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'


    return render_template('register.html', msg=msg, send_register=send_register, view_login=view_login)

@app.route('/index')
def index():
    return render_template('index.html', view_index=view_index, view_option=view_option, view_transactions=view_transactions, send_logout=send_logout)

@app.route('/option')
def option():
    return render_template('option.html', create_option=create_option, view_home=view_home)

@app.route('/createoption', methods=['POST', 'GET'])
def createoption():
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        ticker = request.form['ticker']
        expiration_date = request.form['expiration_date']
        strike = request.form['strike']
        call_put = request.form['call_put']
        buy_sell = request.form['buy_sell']
        notes = request.form['notes']
        result = request.form['result']
    
        return redirect(url_for('success', name=name, quantity=quantity, ticker=ticker, expiration_date=expiration_date, strike=strike, call_put=call_put, buy_sell=buy_sell, notes=notes, result=result))
    else:
        user = request.args.get('name')
        quantity = request.args.get['quantity']
        ticker = request.args.get['ticker']
        expiration_date = request.args.get['expiration_date']
        strike = request.args.get['strike']
        call_put = request.args.get['call_put']
        buy_sell = request.args.get['buy_sell']
        notes = request.args.get['notes']
        result = request.args.get['result']

        return redirect(url_for('success', name=name, quantity=quantity, ticker=ticker, expiration_date=expiration_date, strike=strike, call_put=call_put, buy_sell=buy_sell, notes=notes, result=result))

@app.route('/success/<name>/<quantity>/<ticker>/<expiration_date>/<strike>/<call_put>/<buy_sell>/<notes>/<result>')
def success(name, quantity, ticker, expiration_date, strike, call_put, buy_sell, notes, result):
    try:
        # Get option data
        stock = ticker
        strike = float(strike)
        sub_Day = expiration_date[3:5]
        sub_month = expiration_date[0:2]
        sub_year = expiration_date[-4:]
        notes = unquote(notes)
        result = unquote(result)
    
        Day = int(sub_Day)
        month = int(sub_month)
        year = int(sub_year)

        today = date.today()
        future = date(year,month,Day)
        expiry = future
        
        chain = options.get_options_chain(stock, expiry)

        if call_put == 'Put':   
            s = chain["puts"]['Implied Volatility']
            strikes = chain["puts"]['Strike']
            volume = chain["puts"]['Volume']
            if buy_sell == 'Sell':
                bids = chain["puts"]['Bid']
            if buy_sell == 'Buy':
                bids = chain["puts"]['Ask']    

        if call_put == 'Call':   
            s = chain["calls"]['Implied Volatility']
            strikes = chain["calls"]['Strike']
            volume = chain["calls"]['Volume']
            if buy_sell == 'Sell':
                bids = chain["calls"]['Bid']
            if buy_sell == 'Buy':
                bids = chain["calls"]['Ask']   
               
        s_strikes = pd.DataFrame({'Strike': strikes, 'IV': s, 'Volume': volume, 'Bid': bids})  

        filtered_s_strings = s_strikes[(s_strikes.Strike == strike)]

        r = .05 #0.25
        S = si.get_live_price(stock)
        #K = strike to be set if call or put
        t = float((future - today).days)
        T = t/365
        q = 0.012
        sigma = filtered_s_strings["IV"].apply(lambda x: float(x[:-1]) / 100)
        
        if call_put == 'Put': 
            K = chain["puts"].Strike
            delta = black_scholes_delta(S, K, T, r, sigma, option_type='put')
        if call_put == 'Call':  
            K = chain["calls"].Strike
            delta = black_scholes_delta(S, K, T, r, sigma, option_type='call') 
        
        filtered_s_strings['Delta'] = delta
        float_strike = filtered_s_strings['Strike'].astype('float')
        float_bid = filtered_s_strings['Bid'].astype('float')
        filtered_s_strings['ROR'] = (float_bid / float_strike) * 100

        option_delta = str(filtered_s_strings['Delta'].values[0])
        option_ror = str(filtered_s_strings['ROR'].values[0])
        option_volume = str(filtered_s_strings['Volume'].values[0])
        option_iv = str(filtered_s_strings['IV'].values[0])
        option_bid = str(filtered_s_strings['Bid'].values[0])
    
        str_stock = str(stock)
        str_expiry = str(expiry)
        str_strike = str(strike)
        str_iv = option_iv[:-1] # remove %

        # Get Standard Deviation, Upper, Lower and Mean
        # Fetch the historical data
        app.logger.error("Getting yf.download")
        stock_data = yf.download(ticker, period="1mo")  
        app.logger.error("Got yf.download")
        app.logger.error("Calling standard_dev()")
        close_price, np_std, upper_bound, mean, lower_bound = standard_dev(stock_data, expiry)

        # Market Phase
        # Get the current stock price
        app.logger.error("Getting current_price")
        current_price = stock_data['Close'].iloc[-1]
        current_phase = market_phase(current_price) 

        # Get Buy or Sell Signal
        # Momemtum Crossover:
        app.logger.error("Getting momemtum crossover")
        int_stock_data = stock_data['Close'].astype(int)
        prices_list = int_stock_data.values.tolist()
        df_prices = pd.DataFrame({'price': prices_list})
        data = calculate_momentum_crossover(df_prices, 3, 5) ### what

        # Last row is the most current signal
        # Get the last row
        app.logger.error("Getting momemtum crossover last row")
        last_row = data.iloc[-1]

        # Get the value in the last column of the last row
        app.logger.error("Getting momemtum crossover last column")
        last_row_last_column_value = last_row.iloc[-1]

        app.logger.error("Getting momemtum crossover signal")
        signal = ''
        if last_row_last_column_value == -1:
            signal = 'Sell'
        else:
            signal = 'Buy'

        # Get Price Direction
        app.logger.error("Getting price direction")
        direction = calculate_price_direction(ticker)

        sql = "INSERT INTO OPTIONS_DATA (USER_NAME, QUANTITY, TICKER, EXPIRATION_DATE, STRIKE, CALL_PUT, BUY_SELL, DELTA, VOLUME, BID_ASK, ROR, IV, NOTES, RESULT, DIR, SIG, PHASE, CURRENT_PRICE, STD_DEV, UPPER, MEAN, LOWER) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (name, quantity, str_stock, str_expiry, str_strike, call_put, buy_sell, option_delta, option_volume, option_bid, option_ror, str_iv, notes, result, direction, signal, current_phase, close_price, np_std, upper_bound, mean, lower_bound)

        print('sql:', sql)

        mydb = get_connection()

        mycursor = mydb.cursor()
        
        app.logger.error("/success, mycursor.execute with values", values)
        # Python type Series cannot be converted 
        # looks like current_price
        mycursor.execute(sql, values)

        mydb.commit()

        mycursor.close()
        mydb.close()

        app.logger.error("Returning from /success, going to option_result.html")

        return render_template('option_result.html', view_home=view_home, quantity=quantity, name=name, stock=str_stock, expiry=str_expiry, strike=str_strike, call_put=call_put, buy_sell=buy_sell, delta=option_delta, volume=option_volume, bid=option_bid, ror=option_ror, iv=option_iv, notes=notes, result=result, direction=direction, signal=signal, current_phase=current_phase, current_price=current_price, np_std=np_std, upper_bound=upper_bound, mean=mean, lower_bound=lower_bound)

    except Exception as e:
        return render_template('error.html', view_error=e, view_home=view_home)    

@app.route('/transactions')
def transactions():
    try: 
        # Check to see if there is still an active session
        if 'loggedin' not in session:
            app.logger.error("Session is gone, returning to login")
            return render_template('login.html', view_login=view_login, send_register=send_register)

        sql = "SELECT * FROM OPTIONS_DATA WHERE USER_NAME = '" + session['user_name'] + "'"
        
        mydb = get_connection()

        mycursor = mydb.cursor() 

        mycursor.execute(sql) 

        db = mycursor.fetchall() 

        mycursor.close()
        mydb.close()

        return render_template("transactions.html", dbhtml=db, send_transaction_to_edit=send_transaction_to_edit, view_home=view_home)     
                                  
    except Exception as e: 
        return(str(e))
    
@app.route('/send_transaction/', methods=['POST', 'GET'])
def send_transaction():
    if request.method == 'POST':
        selected_row_id = request.form['selected_row_id']
    else:
        selected_row_id = request.args.get['selected_row_id']

    if selected_row_id == "download":
        try: 
            # Check to see if there is still an active session
            if 'loggedin' not in session:
                app.logger.error("Session is gone, returning to login")
                return render_template('login.html', view_login=view_login, send_register=send_register)
        

            sql = "SELECT * FROM OPTIONS_DATA WHERE USER_NAME = '" + session['user_name'] + "'"
    
            mydb = get_connection()

            mycursor = mydb.cursor() 

            mycursor.execute(sql) 

            db = mycursor.fetchall() 

            # Create a temporary CSV file and serve it for download
            df = pd.DataFrame(db)

            mycursor.close()
            mydb.close()

            return Response(
                df.to_csv(),
                mimetype="text/csv",
                headers={"Content-disposition":
                "attachment; filename=transactions.csv"})                                  
        except Exception as e: 
            return(str(e))
    else:        
        try: 
            mydb = get_connection()
            
            mycursor = mydb.cursor() 

            mycursor.execute("SELECT * FROM OPTIONS_DATA WHERE ID = " + selected_row_id) 

            db = mycursor.fetchall() 

            mycursor.close()
            mydb.close()

            return render_template("edit_transaction.html", dbhtml=db, edit_transaction_to_edit=edit_transaction_to_edit, view_home=view_home)                                   
        except Exception as e: 
            return(str(e))
    
@app.route('/edit_transaction/', methods=['POST', 'GET'])
def edit_transaction():
    if request.method == 'POST':
        operation = request.form['operation']
        row_id = request.form['row_id']
        result = request.form['result']
        notes = request.form['notes']
        quantity = request.form['quantity']
    else:
        operation = request.args.get['operation']
        row_id = request.args.get['row_id']
        result = request.args.get['result']
        notes = request.args.get['notes']
        quantity = request.args.get['quantity']


    if operation == 'Edit':
        try: 
            # Check to see if there is still an active session
            if 'loggedin' not in session:
                app.logger.error("Session is gone, returning to login")
                return render_template('login.html', view_login=view_login, send_register=send_register)
        
            app.logger.error("Edit: getting connection")

            mydb = get_connection()

            mycursor = mydb.cursor() 

            mycursor.execute("UPDATE OPTIONS_DATA SET QUANTITY = '" + quantity + "', NOTES = '" + notes + "', RESULT = '" + result + "' WHERE ID = " + row_id) 

            mydb.commit()

            sql = "SELECT * FROM OPTIONS_DATA WHERE USER_NAME = '" + session['user_name'] + "'"

            mycursor.execute(sql) 

            db = mycursor.fetchall() 

            mycursor.close()
            mydb.close()

            return render_template("transactions.html", dbhtml=db, send_transaction_to_edit=send_transaction_to_edit, view_home=view_home)                                  
        except Exception as e: 
            return(str(e))    
                                      
    if operation == 'Delete':
        try: 
            mydb = get_connection()

            mycursor = mydb.cursor() 

            mycursor.execute("DELETE FROM OPTIONS_DATA" + " WHERE ID = " + row_id) 

            mydb.commit()

            sql = "SELECT * FROM OPTIONS_DATA WHERE USER_NAME = '" + session['user_name'] + "'"

            mycursor.execute(sql) 

            db = mycursor.fetchall() 

            mycursor.close()
            mydb.close()

            return render_template("transactions.html", dbhtml=db, send_transaction_to_edit=send_transaction_to_edit, view_home=view_home)                                  
        except Exception as e: 
            return(str(e))        
    
        
# Entry point
if __name__ == '__main__':
    app.run()
