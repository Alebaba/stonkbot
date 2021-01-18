from stonkbot.stock_analysis import TechnicalAnalysis
import matplotlib.pyplot as plt

alphavantageapikeyfile = open('alpha_vantage_api_keys', 'r')
apikeys = alphavantageapikeyfile.readline() 
alphavantageapikeyfile.close()

ta = TechnicalAnalysis(apikeys=apikeys)

#%% Ticker and date
ticker = 'AAPL'

#%% Price data and technical indicators
ta.get_price_data(ticker=ticker)
ta.get_technical_indicators(ticker=ticker)

#%% Testing bollinger bands
#TODO - Add candlestick to plot
ta.get_bollinger_band_data(ticker=ticker)[1:100].plot()

date = '2020-12-29'
isbollingerbandcrossed, whatwascrossed = ta.bollinger_band_crossed(ticker=ticker, date=date)

print(isbollingerbandcrossed)
print(whatwascrossed)


#%% Testing RSI
#TODO - Plot upper and lower levels (and return those also?)
ta.get_rsi_data(ticker=ticker)[5000:5317].plot()

#TODO - return RSI value also
date = '2020-09-21'
isrsilimitcrossed, whatwascrossed = ta.rsi_limit_crossed(ticker=ticker, date=date)

print(isrsilimitcrossed)
print(whatwascrossed)