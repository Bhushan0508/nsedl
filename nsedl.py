# =============================================================================
# Backtesting strategy - II : Intraday resistance breakout strategy
# Author : Mayank Rasu & Bhushan Gawai
# This strategy checks if the stock has breached 20 day rolling price 
# whether High or Low and based on this buys the stock

#Name is breakout strategy
# 1. Check if the stock has breached the 20 day mean price 

# 2.Buy Condition 
#	a. If todays High has breached 20 Day mean and 
#	b. Volume is 1.5 times the previous day volume
# 3. Sell Condition 
#	a. If todays Low is lesser than the 20 day rolling price
#	b. Volume is 1.5 times the prev day volume 

# 4. Backest and check the CAGR and Sharpe Ratio
# 5. Integrated with fyers.
	

import numpy as np
import pandas as pd
#from alpha_vantage.timeseries import TimeSeries
#import copy
import time
#import config
from fyers_api import fyersModel
from fyers_api import accessToken
#from websocket_background import run_process_background_order_update, run_process_background_symbol_data
import document_file
from selenium import webdriver
#from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
import datetime
import gmailotp
from selenium.webdriver.common.by import By
import os.path
import calendar
#import nsetools
#import requests
#import json

def generate_access_token(auth_code, appId, secret_key):
	appSession = accessToken.SessionModel(client_id=appId, secret_key=secret_key,grant_type="authorization_code")
	appSession.set_token(auth_code)
	response = appSession.generate_token()["access_token"]
	return response

def generate_auth_code():
	url = f"https://api.fyers.in/api/v2/generate-authcode?client_id={client_id}&redirect_uri={redirect_url}&response_type=code&state=state&scope=&nonce="
	#url = f"https://www.google.com"
	#binary_path = GeckoDriverManager().install()
	#print(binary_path)
	driver = webdriver.Chrome()
	
	# driver = webdriver.Firefox(executable_path=r"C:\Users\tradi\.wdm\drivers\geckodriver\win64\v0.30.0\geckodriver.exe")
	driver.get(url)
	time.sleep(3)
	driver.execute_script(f"document.querySelector('[id=fy_client_id]').value = '{username}'")
	driver.execute_script("document.querySelector('[id=clientIdSubmit]').click()")
	#time.sleep(3)
	#driver.execute_script(f"document.querySelector('[id=fy_client_pwd]').value = '{password}'")
	#driver.execute_script("document.querySelector('[id=loginSubmit]').click()")
	#time.sleep(5)
	time.sleep(9)
	otp = gmailotp.getFyersOTP(datetime.datetime.now())
	print(otp)
	driver.find_element(By.ID,"otp-container").find_element(By.ID,"first").send_keys(otp[0])
	driver.find_element(By.ID,"otp-container").find_element(By.ID,"second").send_keys(otp[1])
	driver.find_element(By.ID,"otp-container").find_element(By.ID,"third").send_keys(otp[2])
	driver.find_element(By.ID,"otp-container").find_element(By.ID,"fourth").send_keys(otp[3])
	driver.find_element(By.ID,"otp-container").find_element(By.ID,"fifth").send_keys(otp[4])
	driver.find_element(By.ID,"otp-container").find_element(By.ID,"sixth").send_keys(otp[5])
	driver.execute_script("document.querySelector('[id=confirmOtpSubmit]').click()")
	time.sleep(5)
	#######################OTP######################
	driver.find_element(By.ID,"pin-container").find_element(By.ID,"first").send_keys(pin1[0])
	driver.find_element(By.ID,"pin-container").find_element(By.ID,"second").send_keys(pin1[1])
	driver.find_element(By.ID,"pin-container").find_element(By.ID,"third").send_keys(pin1[2])
	driver.find_element(By.ID,"pin-container").find_element(By.ID,"fourth").send_keys(pin1[3])
	#driver.execute_script("document.querySelector('[id=verifyPinSubmit]').click()")
	#time.sleep(3)
	# Login to gmail
	# Extract the OTP 
	# Input in fyers box
	time.sleep(4)
	#url = input("please enter url...")
	
	newurl = driver.current_url
	auth_code = newurl[newurl.index('auth_code=')+10:newurl.index('&state')]
	driver.quit()
	return auth_code



# Download historical data (monthly) for selected stocks
#config.read_config()
#stocklist  = pd.read_csv(config.stocklistfile)
#stocksymbols = stocklist['Symbol']
#print(stocksymbols.head())
#stocksymbols.drop([0,1],inplace=True,axis=0)
log_path = document_file.log_path
client_id = document_file.client_id
secret_key = document_file.secret_key
redirect_url = document_file.redirect_url
response_type = document_file.response_type
grant_type = document_file.grant_type
username = document_file.username
password = document_file.password
pin1 = document_file.pin1
pin2 = document_file.pin2
pin3 = document_file.pin3
pin4 = document_file.pin4

exchange = "NSE"
quantity = int(100)
timeframe = "5"

def getStartTime():	
	timediff = datetime.timedelta(hours=24*60)
	if datetime.datetime.now().weekday() == 0 :
		from_date = datetime.datetime.now() - timediff*3	
		return from_date.strftime('%Y-%m-%d')

	from_date = datetime.datetime.now() - timediff
	return from_date.strftime('%Y-%m-%d')

from_date = getStartTime()
print ('from date ',from_date)
today = datetime.datetime.now().strftime('%Y-%m-%d') #"2022-03-14"
rsi_overbought = 80
rsi_oversold = 20
buy_traded_stock = []
sell_traded_stock = []
ohlc_intraday = {} # directory with ohlc value for each stock	
def checkfileexist(filename):
	try:
		file_exists = os.path.exists(filename)
		if file_exists:
			
			return file_exists
		else:
			#check file exists in data folder
			fileparts = filename.split('_')
			if len(fileparts) == 3:
				filepath = 'data/'+fileparts[1]+'/'+filename
				file_exists = os.path.exists(filepath)
				if file_exists == False:
					#check folder exists
					datafolderexist = os.path.exists('data')
					if datafolderexist == False:
						os.mkdir('data')
					datefolderexist = os.path.exists('data'+'/'+fileparts[1])
					if datefolderexist == False:
						os.mkdir('data/'+fileparts[1])

					file_exists = os.path.exists(filepath)
					return file_exists
				else:
					return file_exists
			else:
				return False
	except Exception as e:
		print(e)
		return False
def movetodatafolder(filename):
	try:
		fileparts = filename.split('_')
		if len(fileparts) == 3:
			filepath = 'data/'+fileparts[1]
			os.rename(filename,filepath+'/'+filename)
	except Exception as e:
 		print(e)
def downloadData(fyers,symbol,date):
	try:
		
		
		data = {
			"symbol":symbol,
			"resolution":"1",
			"date_format":"1",
			"range_from":date,
			"range_to":date,
			"cont_flag":"0"
		}
		fileName = symbol+'_'+date+'_'+'1min.csv'
		if checkfileexist(fileName) == False:
			response = fyers.history(data=data)
			if response['s'] == 'ok':		
				print("count=",len(response['candles']))
				df = pd.DataFrame(response['candles'])
				
				df.to_csv(fileName,index=False)
				#move file to data folder
				movetodatafolder(fileName)
			#print(df)
		#print(response)
	except Exception as e:
		print(e)
	pass
def getMonthlyExpiryDate():
	today = datetime.date.today()
	# Get the last day of the month
	last_day_of_month = calendar.monthrange(today.year, today.month)[1]

	# Get the last Thursday of the month
	last_thursday = datetime.date(today.year, today.month, last_day_of_month) - datetime.timedelta(days=(last_day_of_month - calendar.weekday(today.year, today.month, last_day_of_month)) % 7)
	return last_thursday.strftime("%y%b").upper()
strike_priceoffset={"NIFTY":50,"FINNIFTY":50,"BANKNIFTY":100}
def nearest_strike(strike_step,n):
    if n % strike_step == 0:
        return n
    else:
        quotient = n // strike_step
        remainder = n % strike_step
        if remainder <= 25:
            return quotient * strike_step
        else:
            return (quotient + 1) * strike_step
def get20StrikePrices(atm_strike,symbol):
    start_strike = atm_strike-strike_priceoffset[symbol]*10
    end_strike = atm_strike+strike_priceoffset[symbol]*10
    strike_price_list = []
    for strike in range(int(start_strike),int(end_strike),strike_priceoffset[symbol]):
        strike_price_list.append(strike)
    print(strike_price_list)
    return strike_price_list
#def getWeeklyExpirySymbols():
    #getweeklyexpirydates
    
def getMonthlyOptionSymbols(symbol,symbolEQ,date):
	#nse = nsetools.Nse()
	#strike_prices = nse.get_active_monthly get_strike_prices(symbol)
	monthly_expiry = getMonthlyExpiryDate()
	#get median strike price 
	filePath = 'data/'+date+'/'+symbolEQ+'_'+date+'_'+'1min.csv'
	if os.path.exists(filePath):
		df = pd.read_csv(filePath)
		df.columns = ['timestamp', 'open', 'high','low','close','volume']
		mean_price = df[['open', 'high', 'low', 'close']].mean(axis=1).mean()
		print (mean_price)
		atm_strike = nearest_strike(strike_priceoffset[symbol],mean_price)
		print('atm_strike:=',atm_strike)
		strikelist = get20StrikePrices(atm_strike,symbol)
		#generate symbols for options
		monthly_symbols =[]
		for strike in strikelist:
			optionssymbol_CE = "NSE:"+symbol+monthly_expiry+str(strike)+'CE'
			optionssymbol_PE = "NSE:"+symbol+monthly_expiry+str(strike)+'PE'
			monthly_symbols.append(optionssymbol_CE)
			monthly_symbols.append(optionssymbol_PE)
		print(monthly_symbols)
		return monthly_symbols
		#strikes_above_mean = strike_prices.loc[strike_prices['strike_price'] > mean_price].head(10)
		#strikes_below_mean = strike_prices.loc[strike_prices['strike_price'] < mean_price].head(10)
		#print("strikes_above_mean -",strikes_above_mean)
		#print("strikes_below_mean -",strikes_below_mean)
def downloadEqFutOptions(fyers,symbol):
	yesterday = datetime.datetime.now() #- datetime.timedelta(days=1)
	#date = datetime.datetime.now().strftime("%Y-%m-%d")
	date = yesterday.strftime("%Y-%m-%d")
	fyersSymbolEq = 'NSE:'+symbol+'-'+'EQ'
	if '-INDEX' in fyersSymbolEq:
		fyersSymbolEq = fyersSymbolEq.replace('-EQ','')
	downloadData(fyers,fyersSymbolEq,date)
	if symbol == 'NIFTY50-INDEX':
		symbol = 'NIFTY'
	if symbol == 'NIFTYBANK-INDEX':
		symbol = 'BANKNIFTY'
	if symbol == 'FINNIFTY-INDEX':
		symbol = 'FINNIFTY'
	# Get the current date
	today = datetime.date.today()
	# Get the last day of the month
	last_day_of_month = calendar.monthrange(today.year, today.month)[1]

	# Get the last Thursday of the month
	last_thursday = datetime.date(today.year, today.month, last_day_of_month) - datetime.timedelta(days=(last_day_of_month - calendar.weekday(today.year, today.month, last_day_of_month)) % 7)

	# Print the last Thursday of the month
	
	fyersSymbolFUT = "NSE:"+symbol+last_thursday.strftime("%y%b").upper()+'FUT'
	print("Futures Symbol ="+fyersSymbolFUT)
	downloadData(fyers,fyersSymbolFUT,date)
	#options
	if symbol == 'NIFTY' or symbol == 'BANKNIFTY' or symbol == 'FINNIFTY':
		monthly_symbols = getMonthlyOptionSymbols(symbol,fyersSymbolEq,date)
		for monthly_symbol in monthly_symbols:
			downloadData(fyers,monthly_symbol,date)
    
	pass
def read_stocklist(filename):
	"""Reads a text file and loads the data into a set.

	Args:
		filename: The name of the text file to read.

	Returns:
		A set containing the data from the text file.
	"""

	with open(filename, "r") as f:
		data = f.read().splitlines()

	set_data = set()
	for line in data:
		set_data.add(line)

	return set_data


	# Example usage:

	set_data = read_text_file_into_set("my_text_file.txt")

	# Print the set data
	print(set_data)
def downloadAllData(fyers):
    stockset = read_stocklist('stocklist.csv')
    for symbol in stockset:
        downloadEqFutOptions(fyers,symbol)
    pass
def getTime():
	return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def main():
	global fyers
	#getOptionSymbols("NIFTY","NSE:NIFTY50-INDEX",'2023-11-15')
	auth_code = generate_auth_code()
	access_token = generate_access_token(auth_code, client_id, secret_key)
	fyers = fyersModel.FyersModel(token=access_token, log_path=log_path, client_id=client_id)
	fyers.token = access_token

	closingtime = int(23) * 60 + int(30)
	orderplacetime = int(10) * 60 + int(36)
	timenow = (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute)
	print(f"Waiting for 10:00 AM , Time Now:{getTime()}")

	while timenow < orderplacetime:
		time.sleep(0.2)
		timenow = (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute)
	print(f"Ready for trading, Time Now:{getTime()}")
	#shortListScrip()
	#processData()
	#backtest()
	#setupSubscription(access_token)
	downloadAllData(fyers)
	while timenow < closingtime:
		time.sleep(1)
		#entryCondition()
		
	
if __name__ == "__main__":
	main()