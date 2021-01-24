from datetime import date
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from api_keys import ALPHA_VANTAGE_API_KEYS

# Alpha vantage limitations: 5 API requests per minute and 500 requests per day
# Date format: YYYY-MM-DD

class TechnicalAnalysis:
    def __init__(self):
        self.apikeyamount = len(ALPHA_VANTAGE_API_KEYS)
        self.currentapikey = ALPHA_VANTAGE_API_KEYS[0]
        self.requestcounter = 0
        self.pricedatas = {}
        self.tidatas = {}
        self.bbdatas = {}
        self.rsidatas = {}
        self.currentdate = date.today().strftime('%Y-%m-%d')
        
        # When technical indicator data was updated last time
        # Used to save API calls
        self.bbdatasupdated = {}
        self.rsidatasupdated = {}
    
    # Calling this method will use 1 API request
    def get_price_data(self, ticker, timeframe='daily'):
        try:
            time = TimeSeries(key=self.currentapikey, output_format='pandas')
            if timeframe == 'daily':
                self.pricedatas[ticker] = time.get_daily(symbol=ticker, outputsize='compact')
            elif timeframe == 'hourly':
                self.pricedatas[ticker] = time.get_hourly(symbol=ticker, outputsize='compact')
        except ValueError:
            print('API call limit exceeded')
    
    # Calling this method will use 1 API request
    def get_technical_indicators(self, ticker):
        try:
            self.tidatas[ticker] = TechIndicators(key=self.currentapikey, output_format='pandas')
        except ValueError:
            print('API call limit exceeded')
     
    # Calling this method may use 1 API request
    def get_bollinger_band_data(self, ticker):
        self.update_date()
        
        if ticker in self.bbdatasupdated:
            if self.bbdatasupdated[ticker] == self.currentdate:
                return self.bbdatas[ticker]

        try:
            self.bbdatas[ticker], metadata = self.tidatas[ticker].get_bbands(symbol=ticker, interval='daily', time_period=20)
            self.bbdatasupdated[ticker] = self.currentdate
        except ValueError:
            print('API call limit exceeded')
                
        return self.bbdatas[ticker]

     # Calling this method may use 1 API request
    def get_rsi_data(self, ticker):
        self.update_date()
        
        if ticker in self.rsidatasupdated:
            if self.rsidatasupdated[ticker] == self.currentdate:
                return self.rsidatas[ticker]

        try:
            self.rsidatas[ticker], metadata = self.tidatas[ticker].get_rsi(symbol=ticker, interval='daily', time_period=20)
            self.rsidatasupdated[ticker] = self.currentdate
        except ValueError:
            print('API call limit exceeded')
            
        return self.rsidatas[ticker]
     
    # Bollinger band is considered to be crossed, if close or open is over the the upper or lower band
    # Calling this method may use 1 API request
    def bollinger_band_crossed(self, ticker, date):
        self.get_bollinger_band_data(ticker=ticker)
        
        if date in self.bbdatas[ticker]:
            lastdaydata_bb = self.bbdatas[ticker][date]
            lastdayopen = self.pricedatas[ticker][0][date]['1. open'][0]
            lastdayclose = self.pricedatas[ticker][0][date]['4. close'][0]
            
            upperbandaverage, lowerbandaverage = 0, 0
            for i in range(0, len(lastdaydata_bb)):
                upperbandaverage += lastdaydata_bb['Real Upper Band'][i]
                lowerbandaverage += lastdaydata_bb['Real Lower Band'][i]
            
            upperbandaverage = upperbandaverage / len(lastdaydata_bb)
            lowerbandaverage = lowerbandaverage / len(lastdaydata_bb)
            
            if (lastdayopen > upperbandaverage or lastdayclose > upperbandaverage):
                return [True, 'Upper band crossed']
            elif (lastdayopen < lowerbandaverage or lastdayclose < lowerbandaverage):
                return [True, 'Lower band crossed']
            else:
                return [False, 'No band crossed']
        else:
            return [False, 'No data for a given day']
    
    # Calling this method may use 1 API request
    def rsi_limit_crossed(self, ticker, date):
        self.get_rsi_data(ticker)
        
        if date in self.rsidatas[ticker]['RSI']:
            if (self.rsidatas[ticker]['RSI'][date] > 70):
                return [True, 'RSI is over 70']
            elif (self.rsidatas[ticker]['RSI'][date] < 30):
                return [True, 'RSI is under 30']
            else:
                return [False, 'RSI is between 30 and 70']
        else:
            return [False, 'No data for a given day']

    def update_date(self):
        self.currentdate = date.today().strftime('%Y-%m-%d')

# TODO - fundamentals
import yfinance as yf