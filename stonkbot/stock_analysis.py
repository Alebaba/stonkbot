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
        
        # When ticker datas were updated last time
        # Used to save API calls
        self.pricedatasupdated = {}
        self.tidatasupdated = {}
        self.bbdatasupdated = {}
        self.rsidatasupdated = {}
    
    # Calling this method will use 1 API request
    def get_price_data(self, ticker, timeframe='daily', forcerefresh=False):
        self.update_date()
        
        if ticker in self.pricedatasupdated and not forcerefresh:
            if self.pricedatasupdated[ticker] == self.currentdate:
                return
        
        try:
            time = TimeSeries(key=self.currentapikey, output_format='pandas')
            if timeframe == 'daily':
                self.pricedatas[ticker] = time.get_daily(symbol=ticker, outputsize='compact')
            elif timeframe == 'hourly':
                self.pricedatas[ticker] = time.get_hourly(symbol=ticker, outputsize='compact')
            self.pricedatasupdated[ticker] = self.currentdate
        except ValueError:
            print('API call limit exceeded')
    
    # Calling this method will use 1 API request
    def get_technical_indicators(self, ticker, forcerefresh=False):
        self.update_date()
        
        if ticker in self.tidatasupdated and not forcerefresh:
            if self.tidatasupdated[ticker] == self.currentdate:
                return
        
        try:
            self.tidatas[ticker] = TechIndicators(key=self.currentapikey, output_format='pandas')
            self.tidatasupdated[ticker] = self.currentdate
        except ValueError:
            print('API call limit exceeded')
     
    # Calling this method may use 2 API requests
    # TODO: check if forcerefresh is working as intended with tidata
    def get_bollinger_band_data(self, ticker, forcerefresh=False):
        self.update_date()
        
        if ticker not in self.tidatasupdated or forcerefresh:
            self.get_technical_indicators(ticker=ticker, forcerefresh=True)
        
        if ticker in self.bbdatasupdated and not forcerefresh:
            if self.bbdatasupdated[ticker] == self.currentdate:
                return self.bbdatas[ticker]

        try:
            self.bbdatas[ticker], metadata = self.tidatas[ticker].get_bbands(symbol=ticker, interval='daily', time_period=20)
            self.bbdatasupdated[ticker] = self.currentdate
        except ValueError:
            print('API call limit exceeded')
        
        if ticker in self.bbdatas:
            return self.bbdatas[ticker]
        else:
            return None

     # Calling this method may use 2 API requests
     # TODO: check if forcerefresh is working as intended with tidata
    def get_rsi_data(self, ticker, forcerefresh=False):
        self.update_date()
        
        if ticker not in self.tidatasupdated or forcerefresh:
            self.get_technical_indicators(ticker=ticker, forcerefresh=True)
        
        if ticker in self.rsidatasupdated and not forcerefresh:
            if self.rsidatasupdated[ticker] == self.currentdate:
                return self.rsidatas[ticker]

        try:
            self.rsidatas[ticker], metadata = self.tidatas[ticker].get_rsi(symbol=ticker, interval='daily', time_period=20)
            self.rsidatasupdated[ticker] = self.currentdate
        except ValueError:
            print('API call limit exceeded')
        
        if ticker in self.rsidatas:
            return self.rsidatas[ticker]
        else:
            return None
     
    # Bollinger band is considered to be crossed, if close or open is over the the upper or lower band
    # Calling this method may use 2 API requests
    def bollinger_band_crossed(self, ticker, date, forcerefresh=False):
        self.get_bollinger_band_data(ticker=ticker, forcerefresh=forcerefresh)
        
        if ticker not in self.pricedatasupdated or forcerefresh:
            self.get_price_data(ticker=ticker, forcerefresh=True)
        
        try:
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
                return [True, 'Upper bollinger band crossed']
            elif (lastdayopen < lowerbandaverage or lastdayclose < lowerbandaverage):
                return [True, 'Lower bollinger band crossed']
            else:
                return [False, 'No band crossed']
        except ZeroDivisionError:
            return [False, 'No data for a given day']
        except KeyError:
            return [False, 'No data for a given day']
        except IndexError:
            return [False, 'No data for a given day']
    
    # Calling this method may use 2 API requests
    def rsi_limit_crossed(self, ticker, date, forcerefresh=False) -> float:
        self.get_rsi_data(ticker, forcerefresh=forcerefresh)
        
        try:
            return self.rsidatas[ticker]['RSI'][date]
        except KeyError:
            return 0.0

    def update_date(self):
        self.currentdate = date.today().strftime('%Y-%m-%d')

# TODO: fundamentals
import yfinance as yf