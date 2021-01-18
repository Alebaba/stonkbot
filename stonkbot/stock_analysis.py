from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators

# Alpha vantage limitations: 5 API requests per minute and 500 requests per day

class TechnicalAnalysis:
    def __init__(self, apikeys):
        self.apikeyamount = len(self.apikeyes)
        self.currentapikey = self.apikeys[0]
        self.requestcounter = 0
        self.pricedatas = {}
        self.tidatas = {}
    
    # Calling this method will use 1 API request
    def get_price_data(self, ticker, timeframe='daily'):
        time = TimeSeries(key=self.currentapikey, output_format='pandas')
        if timeframe == 'daily':
            self.pricedatas[ticker] = time.get_daily(symbol=ticker, outputsize='compact')
        elif timeframe == 'hourly':
            self.pricedatas[ticker] = time.get_hourly(symbol=ticker, outputsize='compact')
    
    # Calling this method will use 1 API request
    def get_technical_inidcators(self, ticker):
        self.tidatas[ticker] = TechIndicators(key=self.currentapikey, output_format='pandas')
     
    # Bollinger band is considered to be crossed, if close or open is over the the upper or lower band
    # Calling this method will use 1 API request
    # Date format: YYYY-MM-DD
    def bollinger_band_crossed(self, ticker, date):
        bbdata, meta_data = self.tidatas[ticker].get_bbands(symbol=ticker, interval='daily', time_period=20)
        
        try:
            lastdaydata_bb = bbdata[date]
            lastdayopen = self.pricedatas[ticker][0][date]['1. open'][0]
            lastdayclose = self.pricedata[ticker][0][date]['4. close'][0]
            
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
        except ZeroDivisionError:
            return [False, 'No data for a given day']
    
    # Calling this method will use 1 API request
    def rsi_limit_crossed(self, ticker, date):
        rsidata = self.tidatas[ticker].get_rsi(symbol=ticker, interval='daily', time_period=20)
        
        if (rsidata[0]['RSI'][date] > 70):
            return [True, 'RSI is over 70']
        elif (rsidata[0]['RSI'][date] < 30):
            return [True, 'RSI is under 30']
        else:
            return [False, 'RSI is between 30 and 70']
