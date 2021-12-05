import yfinance as yf

try:
    sector = yf.Ticker('AAPL').info['sector']
except:
    sector = 'NA'
print(sector)
