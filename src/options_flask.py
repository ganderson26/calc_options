# flask --app options_flask --debug run
# app.logger.info('This is info output')

from flask import Flask, render_template, redirect, url_for, request
from yahoo_fin import options
from yahoo_fin import stock_info as si
import numpy as np
from scipy.stats import norm
import pandas as pd
from datetime import *
import mysql.connector
from urllib.parse import unquote

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

mydb = mysql.connector.connect(
host="localhost",
user=mysql_user,
password="Marathon#262",
database="OPTIONS"
)


def delta_calc(r, q, S, K, T, sigma):
    try:
        d1 = (np.log(S/K)+(r - q +sigma**2/2)*T)/(sigma*np.sqrt(T))

        print('d1', d1) # getting NaN on all for DELL

        r_delta_calc = norm.cdf(d1, 0, 1) 

        print('r_delta_calc=', r_delta_calc)

        r_delta_calc = r_delta_calc[~np.isnan(r_delta_calc)]
        

        for i in range(len(r_delta_calc)):
            r_delta_calc[i] = 1.00 - r_delta_calc[i]

        return r_delta_calc
        
    except Exception as e:
        return render_template('error.html', error=e, view_home=view_home)
    
def delta_calc_calls(r, q, S, K, T, sigma):
    try:
        d1 = ((np.log(S/K)+(r - q +sigma**2/2)*T)/(sigma*np.sqrt(T)) - sigma*np.sqrt(T))


        print('d1', d1) # getting NaN on all for DELL

        r_delta_calc = norm.cdf(d1, 0, 1) 

        print('r_delta_calc=', r_delta_calc)

        r_delta_calc = r_delta_calc[~np.isnan(r_delta_calc)]
        

        for i in range(len(r_delta_calc)):
            r_delta_calc[i] = 1.00 - r_delta_calc[i]

        return r_delta_calc
        
    except Exception as e:
        return render_template('error.html', error=e, view_home=view_home)    
    
def black_scholes_delta(S, K, T, r, sigma, option_type='call'):
    """Calculate the Black-Scholes delta for a call or put option."""

    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    
    if option_type == 'call':
        delta = norm.cdf(d1)
    else:
        delta = norm.cdf(d1) - 1

    delta = delta[~np.isnan(delta)]    

    return delta

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', view_index=view_index, view_option=view_option, view_transactions=view_transactions)

@app.route('/option')
def option():
    return render_template('option.html', view_login=view_login, view_home=view_home)

@app.route('/transactions')
def transactions():
    try: 
        mycursor = mydb.cursor() 
        mycursor.execute("SELECT * FROM OPTIONS_DATA") 
        db = mycursor.fetchall() 
        return render_template("transactions.html", dbhtml=db, send_transaction_to_edit=send_transaction_to_edit, view_home=view_home)                                   
    except Exception as e: 
        return(str(e))
    
@app.route('/send_transaction/', methods=['POST', 'GET'])
def send_transaction():
    if request.method == 'POST':
        selected_row_id = request.form['selected_row_id']
    else:
        selected_row_id = request.args.get['selected_row_id']

    #return "<p>" + selected_row_id + "</p>"
    try: 
        mycursor = mydb.cursor() 
        mycursor.execute("SELECT * FROM OPTIONS_DATA WHERE ID = " + selected_row_id) 
        db = mycursor.fetchall() 
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
    else:
        operation = request.args.get['operation']
        row_id = request.args.get['row_id']
        result = request.args.get['result']
        notes = request.args.get['notes']

    #return "<p>" + operation + "</p>" + "<p>" + row_id + "</p>" + "<p>" + result + "</p>" + "<p>" + notes + "</p>"

    if operation == 'Edit':
        try: 
            mycursor = mydb.cursor() 
            mycursor.execute("UPDATE OPTIONS_DATA SET NOTES = '" + notes + "', RESULT = '" + result + "' WHERE ID = " + row_id) 

            mycursor.execute("SELECT * FROM OPTIONS_DATA") 
            db = mycursor.fetchall() 
            return render_template("transactions.html", dbhtml=db, send_transaction_to_edit=send_transaction_to_edit, view_home=view_home)                                  
        except Exception as e: 
            return(str(e))                                  
    if operation == 'Delete':
        try: 
            mycursor = mydb.cursor() 
            mycursor.execute("DELETE FROM OPTIONS_DATA" + " WHERE ID = " + row_id) 

            mycursor.execute("SELECT * FROM OPTIONS_DATA") 
            db = mycursor.fetchall() 
            return render_template("transactions.html", dbhtml=db, send_transaction_to_edit=send_transaction_to_edit, view_home=view_home)                                  
        except Exception as e: 
            return(str(e))        
    
        

@app.route('/success/<name>/<ticker>/<expiration_date>/<strike>/<call_put>/<buy_sell>/<notes>')
def success(name, ticker, expiration_date, strike, call_put, buy_sell, notes):
    try:
        #return '%s %s %s %s' % (name, ticker, expiration_date, strike)

        stock = ticker
        strike = float(strike)
        sub_Day = expiration_date[3:5]
        sub_month = expiration_date[0:2]
        sub_year = expiration_date[-4:]
        notes = unquote(notes)
    
        Day = int(sub_Day)
        month = int(sub_month)
        year = int(sub_year)

        today = date.today()
        future = date(year,month,Day)
        expiry = future
        str(future - today)
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        options.get_options_chain(stock)
        chain = options.get_options_chain(stock, expiry)

        # Call - Buy or Sell
        # Put - Buy or Sell

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
        
        

        #r = .01 #0.25
        #S = si.get_live_price(stock)
        #K = chain["puts"].Strike
        #t = float((future - today).days)
        #T = t/365
        #q = 0.012

        r = .05 #0.25
        S = si.get_live_price(stock)
        #K = chain["puts"].Strike
        t = float((future - today).days)
        T = t/365
        q = 0.012

        print('filtered_s_strings["IV"]=', filtered_s_strings["IV"])

        sigma = filtered_s_strings["IV"].apply(lambda x: float(x[:-1]) / 100)
        #good to here
        print('r=', r)

        print('S=', S)
        #print('K=', K)
        print('t=', t)
        print('T=', T)
        print('q=', q)
        print('sigma=', sigma.values)
        
        if call_put == 'Put': 
            #delta = delta_calc(r, q, S, K, T, sigma)
            K = chain["puts"].Strike
            delta = black_scholes_delta(S, K, T, r, sigma, option_type='put')
        if call_put == 'Call': 
            #delta = delta_calc_calls(r, q, S, K, T, sigma)   
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

        


    

        mycursor = mydb.cursor()

        str_stock = str(stock)
        str_expiry = str(expiry)
        str_strike = str(strike)

        #local_future = str(year) + '-' + str(month) + '-' + str(Day)
        #str_expiry = local_future
        str_iv = option_iv[:-1] # remove %
        

        sql = "INSERT INTO OPTIONS.OPTIONS_DATA (USER_NAME, TICKER, EXPIRATION_DATE, STRIKE, CALL_PUT, BUY_SELL, DELTA, VOLUME, BID_ASK, ROR, IV, NOTES) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (name, str_stock, str_expiry, str_strike, call_put, buy_sell, option_delta, option_volume, option_bid, option_ror, str_iv, notes)

        #sql = "INSERT INTO OPTIONS.OPTIONS_DATA (USER_NAME, TICKER, EXPIRATION_DATE, STRIKE, CALL_PUT, BUY_SELL, DELTA, VOLUME, BID_ASK, ROR, IV, NOTES) VALUES ('max', 'mstr', '2024-12-20', 300.00, 'PUT', 'SELL', 0.99, 1234.0, 234.0, 1.0, 22.2, 'TESTING')"
        #mycursor.execute(sql)
        
        mycursor.execute(sql, values)

        #mydb.commit()

        #print(mycursor.rowcount, "record inserted.")

        #mydb.close()

        # Replace with a template
        #return "<p>" + str(stock) + "</p>" + "<p>" + str(expiry) + "</p>" + "<p>" + str(strike) + "</p>" + "<p>PUT</p>" + "<p>" + "Delta: " + option_delta + "</p>" + "<p>" + "ROR: " + option_ror + "</p>" + "<p>" + "Volume: " + option_volume + "</p>" + "<p>" + "IV: " + option_iv + "</p>" + "<p>" + "Bid: " + option_bid + "</p>" + "<p>" + "Call or Put: " + call_put + "</p>" + "<p>" + "Buy or Sell: " + buy_sell + "</p>" + "<p>" + "Notes: " + notes + "</p>" +  "<p><a href='http://127.0.0.1:5000/'>Back to Home</a></p>"
        return render_template('option_result.html', view_home=view_home, name=name, stock=str_stock, expiry=str_expiry, strike=str_strike, call_put=call_put, buy_sell=buy_sell, delta=option_delta, volume=option_volume, bid=option_bid, ror=option_ror, iv=option_iv, notes=notes)

    except Exception as e:
        return render_template('error.html', view_error=e, view_home=view_home)    


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        ticker = request.form['ticker']
        expiration_date = request.form['expiration_date']
        strike = request.form['strike']
        call_put = request.form['call_put']
        buy_sell = request.form['buy_sell']
        notes = request.form['notes']
    
        return redirect(url_for('success', name=name, ticker=ticker, expiration_date=expiration_date, strike=strike, call_put=call_put, buy_sell=buy_sell, notes=notes))
    else:
        user = request.args.get('name')
        ticker = request.args.get['ticker']
        expiration_date = request.args.get['expiration_date']
        strike = request.args.get['strike']
        call_put = request.args.get['call_put']
        buy_sell = request.args.get['buy_sell']
        notes = request.args.get['notes']

        return redirect(url_for('success', name=name, ticker=ticker, expiration_date=expiration_date, strike=strike, call_put=call_put, buy_sell=buy_sell, notes=notes))


if __name__ == '__main__':
    app.run()
